import unittest

from a1_cost_tracker.cli import ProviderConfig, _run_provider


class RunProviderTests(unittest.TestCase):
    def test_cost_uses_configured_input_and_output_prices(self) -> None:
        config = ProviderConfig(
            api_key="unused",
            model="test-model",
            input_price_per_m=0.5,
            output_price_per_m=2.0,
        )

        def fake_call(prompt: str, provider_config: ProviderConfig) -> tuple[str, int, int]:
            self.assertEqual(prompt, "prompt")
            self.assertIs(provider_config, config)
            return "reply", 1_000_000, 500_000

        result, elapsed = _run_provider(
            "test",
            config,
            fake_call,
            "prompt",
        )

        self.assertEqual(result["cost_usd"], 1.5)
        self.assertEqual(result["reply"], "reply")
        self.assertGreaterEqual(elapsed, 0)


if __name__ == "__main__":
    unittest.main()
