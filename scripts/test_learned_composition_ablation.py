"""Check the feature/output ablations without running a long training job."""
import unittest

import torch

from scripts.learned_composition import Field, loss_fn, sample_batch, train


class AblationTests(unittest.TestCase):
    def test_output_conversion_and_loss(self):
        batch = sample_batch(32, torch.Generator().manual_seed(19), "cpu")
        for variant in ("cfm_v", "cfm_v_s", "cfm_x", "cfm_x_s"):
            with self.subTest(variant=variant):
                torch.manual_seed(7)
                field = Field(variant, width=8, depth=1)
                m, v = field(batch["xt"], batch["eps"], batch["y"], batch["cond"])
                torch.testing.assert_close(m, batch["xt"] + batch["eps"] * v)
                # The CFM sample identity makes data MSE equal eps^2-weighted velocity MSE.
                data_error = (m - batch["a"]) ** 2
                torch.testing.assert_close(data_error, batch["eps"] ** 2 * (v - batch["u"]) ** 2)
                expected = data_error.mean() if variant.startswith("cfm_x") else ((v - batch["u"]) ** 2).mean()
                torch.testing.assert_close(loss_fn(field, batch, variant), expected)
                self.assertEqual(field.sfeat, variant.endswith("_s"))
                self.assertEqual(field.net.cond_dim, 3 if field.sfeat else 2)

    def test_feature_is_actual_scaled_coordinate(self):
        batch = sample_batch(8, torch.Generator().manual_seed(4), "cpu")
        for variant in ("cfm_v_s", "cfm_x_s"):
            field = Field(variant, width=8, depth=1)
            inputs = []
            hook = field.net.register_forward_pre_hook(lambda module, args: inputs.append(args[2]))
            field(batch["xt"], batch["eps"], batch["y"], batch["cond"])
            hook.remove()
            expected = torch.asinh((1 - batch["eps"]) * batch["xt"] / batch["eps"] ** 2)
            torch.testing.assert_close(inputs[0][:, -1:], expected)

    def test_new_variants_train_and_support_float64_derivatives(self):
        for variant in ("cfm_v_s", "cfm_x"):
            field = Field(variant, width=8, depth=1)
            before = [p.detach().clone() for p in field.parameters()]
            curve = train(field, variant, 10, 16, 3e-3, 0, "cpu", log_every=50)
            self.assertTrue(any(not torch.equal(a, b) for a, b in zip(before, field.parameters())))
            field.double()
            x = torch.tensor([[1e-10]], dtype=torch.float64, requires_grad=True)
            m, v = field(x, torch.full_like(x, 1e-5), torch.ones_like(x), torch.ones_like(x, dtype=torch.bool))
            derivative, = torch.autograd.grad(m.sum(), x)
            self.assertTrue(torch.isfinite(v).all())
            self.assertTrue(torch.isfinite(derivative).all())


if __name__ == "__main__":
    unittest.main()
