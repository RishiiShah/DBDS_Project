import unittest

from seed_catalog import (
    collect_leaf_requirements,
    get_category_tree,
    get_seed_auction_specs,
    get_seed_summary,
)


class SeedCatalogTests(unittest.TestCase):
    def test_expanded_catalog_has_broad_top_level_coverage(self):
        roots = {root["name"] for root in get_category_tree()}
        self.assertTrue(
            {
                "Electronics",
                "Sporting Goods",
                "Home & Kitchen",
                "Fashion",
                "Collectibles",
                "Books & Media",
                "Automotive",
            }.issubset(roots)
        )

    def test_seed_summary_hits_target_volume(self):
        summary = get_seed_summary()
        self.assertGreaterEqual(summary["top_level_category_count"], 8)
        self.assertGreaterEqual(summary["leaf_category_count"], 30)
        self.assertGreaterEqual(summary["auction_count"], 150)

    def test_every_seeded_auction_maps_to_a_leaf_category(self):
        leaf_requirements = collect_leaf_requirements()
        missing = [
            spec["category"]
            for spec in get_seed_auction_specs()
            if spec["category"] not in leaf_requirements
        ]
        self.assertEqual(missing, [])

    def test_seeded_auctions_cover_required_attributes(self):
        leaf_requirements = collect_leaf_requirements()
        invalid_specs = []

        for spec in get_seed_auction_specs():
            required_fields = leaf_requirements[spec["category"]]
            missing_fields = sorted(
                field for field in required_fields if field not in spec["attrs"]
            )
            if missing_fields:
                invalid_specs.append((spec["name"], missing_fields))

        self.assertEqual(invalid_specs, [])

    def test_active_seeded_auctions_cover_longer_periods(self):
        active_days = [
            spec["days_left"]
            for spec in get_seed_auction_specs()
            if spec["status"] == "active"
        ]

        self.assertGreaterEqual(max(active_days), 45)
        self.assertGreaterEqual(sum(1 for days_left in active_days if days_left >= 21), 40)

    def test_electronics_is_seeded_as_largest_category_family(self):
        counts_by_root = {}
        for spec in get_seed_auction_specs():
            counts_by_root[spec["root_category"]] = counts_by_root.get(spec["root_category"], 0) + 1

        electronics_count = counts_by_root["Electronics"]
        self.assertTrue(
            all(
                electronics_count > count
                for root_name, count in counts_by_root.items()
                if root_name != "Electronics"
            )
        )


if __name__ == "__main__":
    unittest.main()
