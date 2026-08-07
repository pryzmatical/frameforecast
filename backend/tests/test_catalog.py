def test_catalog_lists_games_and_tiers(client):
    resp = client.get("/catalog")
    assert resp.status_code == 200
    body = resp.json()

    assert {g["id"] for g in body["games"]} == {
        "skyrim_se",
        "cyberpunk_2077",
        "minecraft_java",
    }
    assert len(body["cpu_tiers"]) == 3
    assert len(body["gpu_tiers"]) == 5
    assert len(body["ram_tiers"]) == 3
    assert len(body["resolutions"]) == 3
    assert len(body["mod_categories"]) >= 5


def test_game_mods_returns_only_that_games_mods(client):
    resp = client.get("/games/skyrim_se/mods")
    assert resp.status_code == 200
    body = resp.json()
    assert body["game_id"] == "skyrim_se"
    assert len(body["mods"]) > 0
    for mod in body["mods"]:
        assert "category_id" in mod


def test_unknown_game_mods_returns_404(client):
    resp = client.get("/games/not_a_real_game/mods")
    assert resp.status_code == 404
