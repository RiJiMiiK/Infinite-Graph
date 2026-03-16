from __future__ import annotations

from types import SimpleNamespace

from src.infinite_graph import gui


def test_window_compute_communities_gdmp2_warning_can_cancel(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("gdmp2")
    )

    calls = []

    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: "GDMP2 estimate warning.",
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


def test_window_compute_communities_em_warning_can_cancel(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("em")
    )

    calls = []

    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: "EM estimate warning.",
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


def test_window_compute_communities_ga_warning_can_cancel(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("ga")
    )

    calls = []

    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: "GA estimate warning.",
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


def test_window_compute_communities_eigenvector_warning_can_cancel(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("eigenvector")
    )

    calls = []

    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: "Eigenvector estimate warning.",
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


def test_window_compute_communities_girvan_newman_warning_can_cancel(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("girvan_newman")
    )

    calls = []

    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: "Girvan-Newman estimate warning.",
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


def test_window_compute_communities_greedy_modularity_warning_can_cancel(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("greedy_modularity")
    )

    calls = []

    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: "Greedy Modularity estimate warning.",
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


def test_window_compute_communities_head_tail_warning_can_cancel(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("head_tail")
    )

    calls = []

    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: "Head/Tail estimate warning.",
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


def test_window_compute_communities_infomap_warning_can_cancel(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("infomap")
    )

    calls = []

    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: "Infomap estimate warning.",
    )
    monkeypatch.setattr(gui.QMessageBox, "warning", lambda *args: gui.QMessageBox.Cancel)
    monkeypatch.setattr(
        gui,
        "run_mono_community_algorithm",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    window._compute_communities()

    assert calls == []
    assert window.community_summary_label.text() == "No community analysis has been run yet."
    window.close()


def test_window_compute_communities_kcut_warning_can_cancel(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("kcut")
    )

    calls = []

    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: "Kcut estimate warning.",
    )
    monkeypatch.setattr(gui.QMessageBox, "warning", lambda *args: gui.QMessageBox.Cancel)
    monkeypatch.setattr(
        gui,
        "run_mono_community_algorithm",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    window._compute_communities()

    assert calls == []
    assert window.community_summary_label.text() == "No community analysis has been run yet."
    window.close()


def test_window_compute_communities_label_propagation_warning_can_cancel(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("label_propagation_cordasco_gargano")
    )

    calls = []

    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: "Label Propagation estimate warning.",
    )
    monkeypatch.setattr(gui.QMessageBox, "warning", lambda *args: gui.QMessageBox.Cancel)
    monkeypatch.setattr(
        gui,
        "run_mono_community_algorithm",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    window._compute_communities()

    assert calls == []
    assert window.community_summary_label.text() == "No community analysis has been run yet."
    window.close()
def test_window_compute_communities_der_warning_can_cancel(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("der")
    )

    calls = []

    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: "DER estimate warning.",
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


def test_window_compute_communities_cpm_warning_can_cancel(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("cpm")
    )

    calls = []

    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: "CPM estimate warning.",
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


def test_window_compute_communities_bayan_warning_can_cancel(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("bayan")
    )

    calls = []

    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: "Restricted Gurobi license detected.",
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


def test_window_compute_communities_bayan_warning_can_continue(
    qapp, sample_result, monkeypatch
) -> None:
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

    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: "Restricted Gurobi license detected.",
    )
    monkeypatch.setattr(
        gui.QMessageBox,
        "warning",
        lambda *args: gui.QMessageBox.Ok,
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

    window._compute_communities()

    assert calls == [(sample_result["community_graph"], "bayan", {})]
    assert "Algorithm: Bayan" in window.community_summary_label.text()
    window.close()


def test_window_community_parameters_ignore_unsupported_field_types(qapp, monkeypatch) -> None:
    window = gui.InfiniteGraphWindow()
    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_parameters",
        lambda algorithm_name: [
            {
                "name": "unsupported",
                "label": "Unsupported",
                "type": "text",
                "default": "x",
            }
        ],
    )

    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("agdl")
    )
    window._refresh_community_parameter_inputs()

    assert window.community_parameters_group.isHidden() is True
    assert window._community_parameter_inputs == {}
    window.close()


def test_window_compute_communities_failure_shows_error(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    errors = []
    monkeypatch.setattr(
        gui,
        "run_mono_community_algorithm",
        lambda graph, algorithm_name: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(gui.QMessageBox, "critical", lambda *args: errors.append(args))

    window._compute_communities()

    assert errors
    assert "No community analysis has been run yet." == window.community_summary_label.text()
    assert window.community_list.count() == 0
    assert "No community selected." == window.community_details.toPlainText()
    window.close()


def test_window_compute_communities_eigenvector_failure_shows_guided_error(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("eigenvector")
    )
    errors = []
    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        gui,
        "run_mono_community_algorithm",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            RuntimeError(
                "Error at src/community/leading_eigenvector.c:567: "
                "No eigenvalues to sufficient accuracy. -- ARPACK error"
            )
        ),
    )
    monkeypatch.setattr(gui.QMessageBox, "critical", lambda *args: errors.append(args))

    window._compute_communities()

    assert errors
    assert "Algorithm: eigenvector" in errors[0][2]
    assert "ARPACK could not compute eigenvalues with sufficient accuracy" in errors[0][2]
    window.close()


def test_window_compute_communities_no_result_or_algorithm(qapp, sample_result) -> None:
    window = gui.InfiniteGraphWindow()

    window._compute_communities()
    assert window.community_summary_label.text() == "No community analysis has been run yet."

    window._current_result = sample_result
    window.community_algorithm_combo.clear()
    window._compute_communities()
    assert window.community_summary_label.text() == "No community analysis has been run yet."
    window.close()


def test_window_compute_communities_with_warning_and_empty_result(
    qapp, sample_result, monkeypatch
) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._set_community_controls_enabled(True)
    window.community_algorithm_combo.setCurrentIndex(
        window.community_algorithm_combo.findData("leiden")
    )

    monkeypatch.setattr(
        gui,
        "run_mono_community_algorithm",
        lambda graph, algorithm_name: SimpleNamespace(
            communities=[],
            method_name="Leiden",
            method_parameters={},
        ),
    )
    monkeypatch.setattr(
        gui,
        "summarize_mono_community_result",
        lambda result: {
            "communities": [],
            "community_count": 0,
            "community_sizes": [],
            "min_size": 0,
            "max_size": 0,
            "average_size": 0.0,
            "node_to_community": {},
            "method_name": "Leiden",
            "parameters": {},
        },
    )
    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_warning",
        lambda name: "The graph was converted to an undirected view for this run.",
    )
    monkeypatch.setattr(
        gui,
        "get_mono_community_algorithm_pre_run_warning",
        lambda *args, **kwargs: None,
    )

    window._compute_communities()

    assert "Adaptation warning:" in window.community_summary_label.text()
    assert window.community_list.count() == 0
    assert window.community_details.toPlainText() == "No community selected."
    window.close()


def test_window_show_selected_community_handles_invalid_items(qapp, sample_result) -> None:
    window = gui.InfiniteGraphWindow()
    window._current_result = sample_result
    window._current_community_summary = {"communities": [["Fire", "Water"]]}

    window._show_selected_community(None)
    assert window.community_details.toPlainText() == "No community selected."

    item = gui.QListWidgetItem("Invalid")
    item.setData(gui.Qt.UserRole, "bad-index")
    window._show_selected_community(item)
    assert window.community_details.toPlainText() == "No community selected."

    item.setData(gui.Qt.UserRole, 99)
    window._show_selected_community(item)
    assert window.community_details.toPlainText() == "No community selected."
    window.close()
