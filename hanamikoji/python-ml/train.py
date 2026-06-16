"""
Self-play training for Hanamikoji using MaskablePPO.

One model plays both sides. After training, save the model and optionally
export to ONNX for loading back into the Go engine.

Usage:
    python train.py
    python train.py --timesteps 2000000 --out hanamikoji_v2
"""
import argparse

from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker

from env import HanamikojiEnv


def mask_fn(env: HanamikojiEnv):
    return env.action_mask()


def train(timesteps: int, out: str):
    env = HanamikojiEnv()
    env = ActionMasker(env, mask_fn)

    model = MaskablePPO(
        "MlpPolicy",
        env,
        verbose=1,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        learning_rate=3e-4,
        policy_kwargs={"net_arch": [64, 64]},
    )

    model.learn(total_timesteps=timesteps)
    model.save(out)
    print(f"Model saved to {out}.zip")
    env.close()


def export_onnx(model_path: str, out: str = "hanamikoji_agent.onnx"):
    """Export a saved model to ONNX so Go can load it via onnxruntime-go."""
    import torch
    from features import OBS_SIZE

    model = MaskablePPO.load(model_path)
    obs = torch.zeros(1, OBS_SIZE)
    torch.onnx.export(
        model.policy,
        obs,
        out,
        input_names=["obs"],
        output_names=["action_logits"],
        opset_version=17,
    )
    print(f"ONNX model saved to {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--timesteps", type=int, default=500_000)
    parser.add_argument("--out", default="hanamikoji_agent")
    parser.add_argument("--export-onnx", action="store_true",
                        help="Export the saved model to ONNX after training")
    args = parser.parse_args()

    train(args.timesteps, args.out)

    if args.export_onnx:
        export_onnx(args.out)
