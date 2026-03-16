from __future__ import annotations

from types import SimpleNamespace

from PySide6.QtWidgets import QDoubleSpinBox

from src.infinite_graph import gui


def test_window_has_communities_tab(qapp) -> None:
    window = gui.InfiniteGraphWindow()
    tab_titles = [window._main_tabs.tabText(index) for index in range(window._main_tabs.count())]
    assert tab_titles == ["Graph", "Info", "Statistics", "Communities"]
    assert window.community_mode_group.title() == "Community analysis"
    assert window.community_summary_group.title() == "Community summary"
    assert window.community_list_group.title() == "Detected communities"
    assert window.community_details_group.title() == "Selected community"
    expected_algorithms = gui.get_mono_community_algorithms()
    assert window.community_algorithm_combo.count() == len(expected_algorithms)
    assert window.community_algorithm_combo.currentData() == "infomap"
    assert [
        window.community_algorithm_combo.itemText(index)
        for index in range(window.community_algorithm_combo.count())
    ] == [str(item["label"]) for item in expected_algorithms]
    assert window.community_compute_button.text() == "Compute communities"
    assert window.community_compute_button.isEnabled() is False
    assert window.community_algorithm_combo.isEnabled() is False
    assert window.community_parameters_group.isHidden() is False
    assert window.community_summary_label.text() == "No community analysis has been run yet."
    assert window.community_details.toPlainText() == "No community selected."
    assert "QComboBox QAbstractItemView" in window.styleSheet()
    window.close()


def test_window_enables_communities_after_generation(qapp, sample_result) -> None:
    window = gui.InfiniteGraphWindow()
    window.input_edit.setText("save.json")
    window._on_generation_finished(
        sample_result,
        {"positions": [], "adj": [], "sizes": [], "brushes": [], "labels": []},
        1.0,
    )
    assert window.community_compute_button.isEnabled() is True
    assert window.community_algorithm_combo.isEnabled() is True
    assert window.community_summary_label.text() == "No community analysis has been run yet."
    window.close()


def test_window_compute_communities_updates_summary_list_and_details(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("agdl")
    )

    calls = []

    def fake_run(graph, algorithm_name, **kwargs):
        calls.append((graph, algorithm_name, kwargs))
        return SimpleNamespace(
            communities=[{"Water", "Fire"}, {"Steam"}],
            method_name="AGDL",
            method_parameters=kwargs,
        )

    monkeypatch.setattr(gui, "run_mono_community_algorithm", fake_run)
    monkeypatch.setattr(
        gui,
        "summarize_mono_community_result",
        lambda result: {
            "communities": [["Fire", "Water"], ["Steam"]],
            "community_count": 2,
            "community_sizes": [2, 1],
            "min_size": 1,
            "max_size": 2,
            "average_size": 1.5,
            "node_to_community": {"Fire": 0, "Water": 0, "Steam": 1},
            "method_name": "AGDL",
            "parameters": {},
        },
    )
    monkeypatch.setattr(gui, "get_mono_community_algorithm_warning", lambda name: None)
    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: None,
    )

    window._community_parameter_inputs["number_communities"].setValue(5)
    window._community_parameter_inputs["kc"].setValue(4)
    window._compute_communities()

    assert calls == [(sample_result["community_graph"], "agdl", {"number_communities": 5, "kc": 4})]
    assert "Algorithm: AGDL" in window.community_summary_label.text()
    assert "Detected communities: 2" in window.community_summary_label.text()
    assert "Parameters:" in window.community_summary_label.text()
    assert "number_communities=5" in window.community_summary_label.text()
    assert "kc=4" in window.community_summary_label.text()
    assert window.community_list.count() == 2
    assert window.community_list.item(0).text() == "Community 1 (2 nodes)"
    assert "Community: 1" in window.community_details.toPlainText()
    assert "Fire" in window.community_details.toPlainText()
    assert "Water" in window.community_details.toPlainText()
    window.close()


def test_window_community_parameters_visibility_updates_with_algorithm_selection(qapp) -> None:
    window = gui.InfiniteGraphWindow()

    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("async_fluid")
    )
    assert window.community_parameters_group.isHidden() is False
    assert set(window._community_parameter_inputs) == {"k"}

    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("agdl")
    )
    assert window.community_parameters_group.isHidden() is False
    assert set(window._community_parameter_inputs) == {"number_communities", "kc"}

    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("belief")
    )
    assert window.community_parameters_group.isHidden() is False
    assert set(window._community_parameter_inputs) == {
        "max_it",
        "eps",
        "reruns_if_not_conv",
        "threshold",
        "q_max",
    }
    assert isinstance(window._community_parameter_inputs["eps"], QDoubleSpinBox)
    assert isinstance(window._community_parameter_inputs["threshold"], QDoubleSpinBox)

    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("cpm")
    )
    assert window.community_parameters_group.isHidden() is False
    assert set(window._community_parameter_inputs) == {"resolution_parameter"}
    assert isinstance(
        window._community_parameter_inputs["resolution_parameter"], QDoubleSpinBox
    )

    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("der")
    )
    assert window.community_parameters_group.isHidden() is False
    assert set(window._community_parameter_inputs) == {
        "walk_len",
        "threshold",
        "iter_bound",
    }
    assert isinstance(window._community_parameter_inputs["threshold"], QDoubleSpinBox)

    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("em")
    )
    assert window.community_parameters_group.isHidden() is False
    assert set(window._community_parameter_inputs) == {"k"}

    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("ga")
    )
    assert window.community_parameters_group.isHidden() is False
    assert set(window._community_parameter_inputs) == {
        "population",
        "generation",
        "r",
    }
    assert isinstance(window._community_parameter_inputs["r"], QDoubleSpinBox)

    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("gdmp2")
    )
    assert window.community_parameters_group.isHidden() is False
    assert set(window._community_parameter_inputs) == {"min_threshold"}
    assert isinstance(window._community_parameter_inputs["min_threshold"], QDoubleSpinBox)

    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("girvan_newman")
    )
    assert window.community_parameters_group.isHidden() is False
    assert set(window._community_parameter_inputs) == {"level"}

    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("greedy_modularity")
    )
    assert window.community_parameters_group.isHidden() is True
    assert window._community_parameter_inputs == {}

    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("kcut")
    )
    assert window.community_parameters_group.isHidden() is False
    assert set(window._community_parameter_inputs) == {"kmax"}

    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("head_tail")
    )
    assert window.community_parameters_group.isHidden() is False
    assert set(window._community_parameter_inputs) == {"head_tail_ratio"}
    assert isinstance(window._community_parameter_inputs["head_tail_ratio"], QDoubleSpinBox)
    window.close()


def test_window_compute_communities_supports_async_fluid_parameters(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("async_fluid")
    )

    calls = []

    def fake_run(graph, algorithm_name, **kwargs):
        calls.append((graph, algorithm_name, kwargs))
        return SimpleNamespace(
            communities=[{"Water", "Fire"}, {"Steam"}],
            method_name="Fluid",
            method_parameters=kwargs,
        )

    monkeypatch.setattr(gui, "run_mono_community_algorithm", fake_run)
    monkeypatch.setattr(
        gui,
        "summarize_mono_community_result",
        lambda result: {
            "communities": [["Fire", "Water"], ["Steam"]],
            "community_count": 2,
            "community_sizes": [2, 1],
            "min_size": 1,
            "max_size": 2,
            "average_size": 1.5,
            "node_to_community": {"Fire": 0, "Water": 0, "Steam": 1},
            "method_name": "Fluid",
            "parameters": result.method_parameters,
        },
    )
    monkeypatch.setattr(gui, "get_mono_community_algorithm_warning", lambda name: None)
    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: None,
    )

    window._community_parameter_inputs["k"].setValue(3)
    window._compute_communities()

    assert calls == [(sample_result["community_graph"], "async_fluid", {"k": 3})]
    assert "Algorithm: Async Fluid" in window.community_summary_label.text()
    assert "Method name: Fluid" in window.community_summary_label.text()
    assert "Parameters:" in window.community_summary_label.text()
    assert "k=3" in window.community_summary_label.text()
    window.close()


def test_window_compute_communities_async_fluid_warning_can_cancel(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("async_fluid")
    )

    calls = []

    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: "Async Fluid estimate warning.",
    )
    monkeypatch.setattr(
        gui.QMessageBox,
        "warning",
        lambda *args: gui.QMessageBox.Cancel,
    )
    monkeypatch.setattr(
        gui,
        "run_mono_community_algorithm",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    window._compute_communities()

    assert calls == []
    assert window.community_summary_label.text() == "No community analysis has been run yet."
    window.close()


def test_window_compute_communities_supports_bayan(qapp, sample_result, monkeypatch) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("bayan")
    )

    calls = []

    def fake_run(graph, algorithm_name, **kwargs):
        calls.append((graph, algorithm_name, kwargs))
        return SimpleNamespace(
            communities=[{"Water", "Fire"}, {"Steam"}],
            method_name="Bayan",
            method_parameters=kwargs,
        )

    monkeypatch.setattr(gui, "run_mono_community_algorithm", fake_run)
    monkeypatch.setattr(
        gui,
        "summarize_mono_community_result",
        lambda result: {
            "communities": [["Fire", "Water"], ["Steam"]],
            "community_count": 2,
            "community_sizes": [2, 1],
            "min_size": 1,
            "max_size": 2,
            "average_size": 1.5,
            "node_to_community": {"Fire": 0, "Water": 0, "Steam": 1},
            "method_name": "Bayan",
            "parameters": result.method_parameters,
        },
    )
    monkeypatch.setattr(gui, "get_mono_community_algorithm_warning", lambda name: None)
    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: None,
    )

    window._compute_communities()

    assert calls == [(sample_result["community_graph"], "bayan", {})]
    assert "Algorithm: Bayan" in window.community_summary_label.text()
    assert "Method name: Bayan" in window.community_summary_label.text()
    assert "Detected communities: 2" in window.community_summary_label.text()
    assert "Parameters:" not in window.community_summary_label.text()
    window.close()


def test_window_compute_communities_supports_belief_parameters(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("belief")
    )

    calls = []

    def fake_run(graph, algorithm_name, **kwargs):
        calls.append((graph, algorithm_name, kwargs))
        return SimpleNamespace(
            communities=[{"Water", "Fire"}, {"Steam"}],
            method_name="Belief",
            method_parameters=kwargs,
        )

    monkeypatch.setattr(gui, "run_mono_community_algorithm", fake_run)
    monkeypatch.setattr(
        gui,
        "summarize_mono_community_result",
        lambda result: {
            "communities": [["Fire", "Water"], ["Steam"]],
            "community_count": 2,
            "community_sizes": [2, 1],
            "min_size": 1,
            "max_size": 2,
            "average_size": 1.5,
            "node_to_community": {"Fire": 0, "Water": 0, "Steam": 1},
            "method_name": "Belief",
            "parameters": result.method_parameters,
        },
    )
    monkeypatch.setattr(gui, "get_mono_community_algorithm_warning", lambda name: None)
    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: None,
    )

    window._community_parameter_inputs["max_it"].setValue(150)
    window._community_parameter_inputs["eps"].setValue(0.0012)
    window._community_parameter_inputs["reruns_if_not_conv"].setValue(3)
    window._community_parameter_inputs["threshold"].setValue(0.015)
    window._community_parameter_inputs["q_max"].setValue(9)
    window._compute_communities()

    assert calls == [
        (
            sample_result["community_graph"],
            "belief",
            {
                "max_it": 150,
                "eps": 0.0012,
                "reruns_if_not_conv": 3,
                "threshold": 0.015,
                "q_max": 9,
            },
        )
    ]
    assert "Algorithm: Belief" in window.community_summary_label.text()
    assert "Method name: Belief" in window.community_summary_label.text()
    assert "Parameters:" in window.community_summary_label.text()
    assert "eps=0.0012" in window.community_summary_label.text()
    assert "q_max=9" in window.community_summary_label.text()
    window.close()


def test_window_compute_communities_supports_cpm_parameters(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("cpm")
    )

    calls = []

    def fake_run(graph, algorithm_name, **kwargs):
        calls.append((graph, algorithm_name, kwargs))
        return SimpleNamespace(
            communities=[{"Water", "Fire"}, {"Steam"}],
            method_name="CPM",
            method_parameters=kwargs,
        )

    monkeypatch.setattr(gui, "run_mono_community_algorithm", fake_run)
    monkeypatch.setattr(
        gui,
        "summarize_mono_community_result",
        lambda result: {
            "communities": [["Fire", "Water"], ["Steam"]],
            "community_count": 2,
            "community_sizes": [2, 1],
            "min_size": 1,
            "max_size": 2,
            "average_size": 1.5,
            "node_to_community": {"Fire": 0, "Water": 0, "Steam": 1},
            "method_name": "CPM",
            "parameters": result.method_parameters,
        },
    )
    monkeypatch.setattr(gui, "get_mono_community_algorithm_warning", lambda name: None)
    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: None,
    )

    window._community_parameter_inputs["resolution_parameter"].setValue(2.5)
    window._compute_communities()

    assert calls == [
        (
            sample_result["community_graph"],
            "cpm",
            {"resolution_parameter": 2.5},
        )
    ]
    assert "Algorithm: CPM" in window.community_summary_label.text()
    assert "Method name: CPM" in window.community_summary_label.text()
    assert "resolution_parameter=2.5" in window.community_summary_label.text()
    window.close()


def test_window_compute_communities_supports_der_parameters(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("der")
    )

    calls = []

    def fake_run(graph, algorithm_name, **kwargs):
        calls.append((graph, algorithm_name, kwargs))
        return SimpleNamespace(
            communities=[{"Water", "Fire"}, {"Steam"}],
            method_name="DER",
            method_parameters=kwargs,
        )

    monkeypatch.setattr(gui, "run_mono_community_algorithm", fake_run)
    monkeypatch.setattr(
        gui,
        "summarize_mono_community_result",
        lambda result: {
            "communities": [["Fire", "Water"], ["Steam"]],
            "community_count": 2,
            "community_sizes": [2, 1],
            "min_size": 1,
            "max_size": 2,
            "average_size": 1.5,
            "node_to_community": {"Fire": 0, "Water": 0, "Steam": 1},
            "method_name": "DER",
            "parameters": result.method_parameters,
        },
    )
    monkeypatch.setattr(gui, "get_mono_community_algorithm_warning", lambda name: None)
    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: None,
    )

    window._community_parameter_inputs["walk_len"].setValue(4)
    window._community_parameter_inputs["threshold"].setValue(0.00042)
    window._community_parameter_inputs["iter_bound"].setValue(60)
    window._compute_communities()

    assert calls == [
        (
            sample_result["community_graph"],
            "der",
            {
                "walk_len": 4,
                "threshold": 0.00042,
                "iter_bound": 60,
            },
        )
    ]
    assert "Algorithm: DER" in window.community_summary_label.text()
    assert "Method name: DER" in window.community_summary_label.text()
    assert "walk_len=4" in window.community_summary_label.text()
    assert "threshold=0.00042" in window.community_summary_label.text()
    assert "iter_bound=60" in window.community_summary_label.text()
    window.close()


def test_window_compute_communities_supports_eigenvector(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("eigenvector")
    )

    calls = []

    def fake_run(graph, algorithm_name, **kwargs):
        calls.append((graph, algorithm_name, kwargs))
        return SimpleNamespace(
            communities=[{"Water", "Fire"}, {"Steam"}],
            method_name="Eigenvector",
            method_parameters=kwargs,
        )

    monkeypatch.setattr(gui, "run_mono_community_algorithm", fake_run)
    monkeypatch.setattr(
        gui,
        "summarize_mono_community_result",
        lambda result: {
            "communities": [["Fire", "Water"], ["Steam"]],
            "community_count": 2,
            "community_sizes": [2, 1],
            "min_size": 1,
            "max_size": 2,
            "average_size": 1.5,
            "node_to_community": {"Fire": 0, "Water": 0, "Steam": 1},
            "method_name": "Eigenvector",
            "parameters": result.method_parameters,
        },
    )
    monkeypatch.setattr(gui, "get_mono_community_algorithm_warning", lambda name: None)
    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: None,
    )

    window._compute_communities()

    assert calls == [(sample_result["community_graph"], "eigenvector", {})]
    assert "Algorithm: Eigenvector" in window.community_summary_label.text()
    assert "Method name: Eigenvector" in window.community_summary_label.text()
    assert "Detected communities: 2" in window.community_summary_label.text()
    assert "Parameters:" not in window.community_summary_label.text()
    window.close()


def test_window_compute_communities_supports_em_parameters(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("em")
    )

    calls = []

    def fake_run(graph, algorithm_name, **kwargs):
        calls.append((graph, algorithm_name, kwargs))
        return SimpleNamespace(
            communities=[{"Water", "Fire"}, {"Steam"}],
            method_name="EM",
            method_parameters=kwargs,
        )

    monkeypatch.setattr(gui, "run_mono_community_algorithm", fake_run)
    monkeypatch.setattr(
        gui,
        "summarize_mono_community_result",
        lambda result: {
            "communities": [["Fire", "Water"], ["Steam"]],
            "community_count": 2,
            "community_sizes": [2, 1],
            "min_size": 1,
            "max_size": 2,
            "average_size": 1.5,
            "node_to_community": {"Fire": 0, "Water": 0, "Steam": 1},
            "method_name": "EM",
            "parameters": result.method_parameters,
        },
    )
    monkeypatch.setattr(gui, "get_mono_community_algorithm_warning", lambda name: None)
    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: None,
    )

    window._community_parameter_inputs["k"].setValue(4)
    window._compute_communities()

    assert calls == [(sample_result["community_graph"], "em", {"k": 4})]
    assert "Algorithm: EM" in window.community_summary_label.text()
    assert "Method name: EM" in window.community_summary_label.text()
    assert "k=4" in window.community_summary_label.text()
    window.close()


def test_window_compute_communities_supports_ga_parameters(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("ga")
    )

    calls = []

    def fake_run(graph, algorithm_name, **kwargs):
        calls.append((graph, algorithm_name, kwargs))
        return SimpleNamespace(
            communities=[{"Water", "Fire"}, {"Steam"}],
            method_name="ga",
            method_parameters=kwargs,
        )

    monkeypatch.setattr(gui, "run_mono_community_algorithm", fake_run)
    monkeypatch.setattr(
        gui,
        "summarize_mono_community_result",
        lambda result: {
            "communities": [["Fire", "Water"], ["Steam"]],
            "community_count": 2,
            "community_sizes": [2, 1],
            "min_size": 1,
            "max_size": 2,
            "average_size": 1.5,
            "node_to_community": {"Fire": 0, "Water": 0, "Steam": 1},
            "method_name": "ga",
            "parameters": result.method_parameters,
        },
    )
    monkeypatch.setattr(gui, "get_mono_community_algorithm_warning", lambda name: None)
    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: None,
    )

    window._community_parameter_inputs["population"].setValue(123)
    window._community_parameter_inputs["generation"].setValue(45)
    window._community_parameter_inputs["r"].setValue(2.3)
    window._compute_communities()

    assert calls == [
        (
            sample_result["community_graph"],
            "ga",
            {"population": 123, "generation": 45, "r": 2.3},
        )
    ]
    assert "Algorithm: GA" in window.community_summary_label.text()
    assert "Method name: ga" in window.community_summary_label.text()
    assert "population=123" in window.community_summary_label.text()
    assert "generation=45" in window.community_summary_label.text()
    assert "r=2.3" in window.community_summary_label.text()
    window.close()


def test_window_compute_communities_supports_gdmp2_parameters(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("gdmp2")
    )

    calls = []

    def fake_run(graph, algorithm_name, **kwargs):
        calls.append((graph, algorithm_name, kwargs))
        return SimpleNamespace(
            communities=[{"Water", "Fire"}, {"Steam"}],
            method_name="GDMP2",
            method_parameters=kwargs,
        )

    monkeypatch.setattr(gui, "run_mono_community_algorithm", fake_run)
    monkeypatch.setattr(
        gui,
        "summarize_mono_community_result",
        lambda result: {
            "communities": [["Fire", "Water"], ["Steam"]],
            "community_count": 2,
            "community_sizes": [2, 1],
            "min_size": 1,
            "max_size": 2,
            "average_size": 1.5,
            "node_to_community": {"Fire": 0, "Water": 0, "Steam": 1},
            "method_name": "GDMP2",
            "parameters": result.method_parameters,
        },
    )
    monkeypatch.setattr(gui, "get_mono_community_algorithm_warning", lambda name: None)
    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: None,
    )

    window._community_parameter_inputs["min_threshold"].setValue(0.42)
    window._compute_communities()

    assert calls == [
        (
            sample_result["community_graph"],
            "gdmp2",
            {"min_threshold": 0.42},
        )
    ]
    assert "Algorithm: GDMP2" in window.community_summary_label.text()
    assert "Method name: GDMP2" in window.community_summary_label.text()
    assert "min_threshold=0.42" in window.community_summary_label.text()
    window.close()


def test_window_compute_communities_supports_girvan_newman_parameters(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("girvan_newman")
    )

    calls = []

    def fake_run(graph, algorithm_name, **kwargs):
        calls.append((graph, algorithm_name, kwargs))
        return SimpleNamespace(
            communities=[{"Water", "Fire"}, {"Steam"}],
            method_name="Girvan-Newman",
            method_parameters=kwargs,
        )

    monkeypatch.setattr(gui, "run_mono_community_algorithm", fake_run)
    monkeypatch.setattr(
        gui,
        "summarize_mono_community_result",
        lambda result: {
            "communities": [["Fire", "Water"], ["Steam"]],
            "community_count": 2,
            "community_sizes": [2, 1],
            "min_size": 1,
            "max_size": 2,
            "average_size": 1.5,
            "node_to_community": {"Fire": 0, "Water": 0, "Steam": 1},
            "method_name": "Girvan-Newman",
            "parameters": result.method_parameters,
        },
    )
    monkeypatch.setattr(gui, "get_mono_community_algorithm_warning", lambda name: None)
    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: None,
    )

    window._community_parameter_inputs["level"].setValue(4)
    window._compute_communities()

    assert calls == [
        (
            sample_result["community_graph"],
            "girvan_newman",
            {"level": 4},
        )
    ]
    assert "Algorithm: Girvan-Newman" in window.community_summary_label.text()
    assert "Method name: Girvan-Newman" in window.community_summary_label.text()
    assert "level=4" in window.community_summary_label.text()
    window.close()


def test_window_compute_communities_supports_greedy_modularity(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("greedy_modularity")
    )

    calls = []

    def fake_run(graph, algorithm_name, **kwargs):
        calls.append((graph, algorithm_name, kwargs))
        return SimpleNamespace(
            communities=[{"Water", "Fire"}, {"Steam"}],
            method_name="Greedy Modularity",
            method_parameters=kwargs,
        )

    monkeypatch.setattr(gui, "run_mono_community_algorithm", fake_run)
    monkeypatch.setattr(
        gui,
        "summarize_mono_community_result",
        lambda result: {
            "communities": [["Fire", "Water"], ["Steam"]],
            "community_count": 2,
            "community_sizes": [2, 1],
            "min_size": 1,
            "max_size": 2,
            "average_size": 1.5,
            "node_to_community": {"Fire": 0, "Water": 0, "Steam": 1},
            "method_name": "Greedy Modularity",
            "parameters": result.method_parameters,
        },
    )
    monkeypatch.setattr(gui, "get_mono_community_algorithm_warning", lambda name: None)
    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: None,
    )

    window._compute_communities()

    assert calls == [(sample_result["community_graph"], "greedy_modularity", {})]
    assert "Algorithm: Greedy Modularity" in window.community_summary_label.text()
    assert "Method name: Greedy Modularity" in window.community_summary_label.text()
    assert "Detected communities: 2" in window.community_summary_label.text()
    assert "Parameters:" not in window.community_summary_label.text()
    window.close()


def test_window_compute_communities_supports_head_tail_parameters(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("head_tail")
    )

    calls = []

    def fake_run(graph, algorithm_name, **kwargs):
        calls.append((graph, algorithm_name, kwargs))
        return SimpleNamespace(
            communities=[{"Water", "Fire"}, {"Steam"}],
            method_name="Head/Tail",
            method_parameters=kwargs,
        )

    monkeypatch.setattr(gui, "run_mono_community_algorithm", fake_run)
    monkeypatch.setattr(
        gui,
        "summarize_mono_community_result",
        lambda result: {
            "communities": [["Fire", "Water"], ["Steam"]],
            "community_count": 2,
            "community_sizes": [2, 1],
            "min_size": 1,
            "max_size": 2,
            "average_size": 1.5,
            "node_to_community": {"Fire": 0, "Water": 0, "Steam": 1},
            "method_name": "Head/Tail",
            "parameters": result.method_parameters,
        },
    )
    monkeypatch.setattr(gui, "get_mono_community_algorithm_warning", lambda name: None)
    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: None,
    )

    window._community_parameter_inputs["head_tail_ratio"].setValue(0.8)
    window._compute_communities()

    assert calls == [
        (
            sample_result["community_graph"],
            "head_tail",
            {"head_tail_ratio": 0.8},
        )
    ]
    assert "Algorithm: Head/Tail" in window.community_summary_label.text()
    assert "Method name: Head/Tail" in window.community_summary_label.text()
    assert "head_tail_ratio=0.8" in window.community_summary_label.text()
    window.close()


def test_window_compute_communities_supports_kcut_parameters(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("kcut")
    )

    calls = []

    def fake_run(graph, algorithm_name, **kwargs):
        calls.append((graph, algorithm_name, kwargs))
        return SimpleNamespace(
            communities=[{"Water", "Fire"}, {"Steam"}],
            method_name="Kcut",
            method_parameters=kwargs,
        )

    monkeypatch.setattr(gui, "run_mono_community_algorithm", fake_run)
    monkeypatch.setattr(
        gui,
        "summarize_mono_community_result",
        lambda result: {
            "communities": [["Fire", "Water"], ["Steam"]],
            "community_count": 2,
            "community_sizes": [2, 1],
            "min_size": 1,
            "max_size": 2,
            "average_size": 1.5,
            "node_to_community": {"Fire": 0, "Water": 0, "Steam": 1},
            "method_name": "Kcut",
            "parameters": result.method_parameters,
        },
    )
    monkeypatch.setattr(gui, "get_mono_community_algorithm_warning", lambda name: None)
    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: None,
    )

    window._community_parameter_inputs["kmax"].setValue(6)
    window._compute_communities()

    assert calls == [(sample_result["community_graph"], "kcut", {"kmax": 6})]
    assert "Algorithm: Kcut" in window.community_summary_label.text()
    assert "Method name: Kcut" in window.community_summary_label.text()
    assert "kmax=6" in window.community_summary_label.text()
    window.close()
