## Search State

- **Seed**: 9
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | align → descend → contact → retract → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.2451 | 0.86 | ❌ rejected |
| 12 | align → descend → contact → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 10 | -0.2192 | 0.85 | ❌ rejected |
| 11 | align → descend → contact → retract → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | force_threshold_switch | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.1424 | 0.87 | ✅ accepted |
| 10 | align → descend → contact → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | 7 | 0.1799 | 0.85 | ❌ rejected |
| 9 | align → approach → contact → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | 7 | 0.1804 | 0.85 | ❌ rejected |

**Proposal policy**: task_score is 0.86 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: peg_insert
- Frozen realised-scene SHA-256: `d30c452da2a3cff083d30694df03632a9bb782339e47c14383f7124ad9a32464`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5296199363176067, -0.017054623272995572, 0.08]
- Frozen socket pose: [0.5296199363176067, -0.017054623272995572, 0.025] (static fixture for this episode)
- Goal object position: (0.5296199363176067, -0.017054623272995572, 0.025)
- Object initial pose: (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Channel axis: `(0.0, 0.0, -1.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

## Scene Entities

robot:
  model: panda_peg
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: peg_socket
    role: fixture
    dynamics: static
    geometry: box_with_hole
    base_dimensions_m: [0.12, 0.12, 0.05]
    hole_entry_height_m: 0.08
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    note: peg is a fixed end-effector attachment on the panda_peg arm
task_landmarks:
  frozen_object_start: [0.504, -0, 0.3403]
  frozen_task_target: [0.5296, -0.0171, 0.08]
  frozen_socket_position: [0.5296, -0.0171, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5296199363176067, -0.017054623272995572, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5296199363176067, -0.017054623272995572, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: d30c452da2a3cff083d30694df03632a9bb782339e47c14383f7124ad9a32464

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| align | object | (0.00, 0.00, 0.12) | distance | — |
| approach | object | (0.00, 0.00, 0.09) | distance | — |
| contact | object | (0.00, 0.00, 0.07) | distance | — |
| insert | object | (0.00, 0.00, 0.06) | distance | — |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=-0.245) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
phases:
- id: align_above
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.12
    tolerance: 0.01
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: align
- id: approach_entry
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.005
    tolerance: 0.005
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.0
  subtask_id: approach
- id: contact_rim
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - -0.005
    tolerance: 0.005
  parameters:
    probe_force:
      type: scalar
      range:
      - 3.0
      - 15.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
        mode: add
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.003
    - 0.003
    - 0.0
  subtask_id: contact
- id: lift_off_contact
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.01
    tolerance: 0.005
- id: insert_down
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    insert_depth:
      type: scalar
      range:
      - 0.04
      - 0.07
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insert_force_guard_threshold:
      type: scalar
      range:
      - 15.0
      - 40.0
      default: 35.0
      binds_to:
      - path: guards.high_force_guard.threshold
        mode: replace
    insert_speed:
      type: scalar
      range:
      - 0.005
      - 0.04
      default: 0.015
      binds_to:
      - path: generator.speed
        mode: replace
    retry_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.003
      binds_to:
      - path: retry.offset.x
        mode: replace
    retry_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.003
      binds_to:
      - path: retry.offset.y
        mode: replace
  guards:
  - id: high_force_guard
    when: during_phase
    predicate: force_below
    threshold: 35.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.003
    - 0.003
    - 0.0
  subtask_id: insert

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align_above** (`align`)
  - target: source=yaml, anchor=task_goal, entity=peg_socket, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
- **approach_entry** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=peg_socket, offset=[0.0, 0.0, 0.005], tolerance=0.005
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.0, 0.0]
- **contact_rim** (`contact`)
  - target: source=yaml, anchor=task_goal, entity=peg_socket, offset=[0.0, 0.0, -0.005], tolerance=0.005
  - parameter_bindings:
    - probe_force: status=consumed; consumers=termination.force_threshold (add)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.003, 0.003, 0.0]
- **lift_off_contact** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.01], tolerance=0.005
  - parameter_bindings: none
- **insert_down** (`insert`)
  - target: source=yaml, anchor=task_goal, entity=peg_socket, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.05, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - insert_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insert_force_guard_threshold: status=consumed; consumers=guards.high_force_guard.threshold (replace)
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - retry_offset_x: status=consumed; consumers=retry.offset.x (replace)
    - retry_offset_y: status=consumed; consumers=retry.offset.y (replace)
  - guards:
    - id=high_force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=35.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.003, 0.003, 0.0]

## Design Metrics

- **Composite score**: -0.245
- **task_score** (E): 0.860
- **fitness_score**: 0.345  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.590

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_above | 1.00 | 0.00 | 0.0977 |
| descend_to_entry | 1.00 | 0.00 | 0.1204 |
| contact_rim | 0.00 | 0.00 | 0.0191 |
| lift_off_contact | 1.00 | 0.00 | 0.0057 |
| insert_down | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_above | align | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, -0.012, 0.208) | (0.504, -0.000, 0.340)→(0.516, -0.012, 0.247) | 0.260→0.170 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_to_entry | descend | 1.00 / step_budget | (0.508, -0.012, 0.208)→(0.508, -0.013, 0.087) | (0.516, -0.012, 0.247)→(0.520, -0.013, 0.125) | 0.170→0.058 | 0.00 / 0.000 | 0.000 | 0.000 |
| contact_rim | contact | 0.00 / step_budget | (0.508, -0.013, 0.087)→(0.508, -0.013, 0.068) | (0.520, -0.013, 0.125)→(0.508, -0.013, 0.108) | 0.058→0.045 | 0.00 / 0.000 | 0.000 | 0.000 |
| lift_off_contact | retract | 1.00 / step_budget | (0.508, -0.013, 0.068)→(0.504, -0.013, 0.073) | (0.508, -0.013, 0.108)→(0.504, -0.013, 0.113) | 0.045→0.047 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_down | insert | 0.00 / guard_failure | (0.504, -0.013, 0.050)→(0.504, -0.013, 0.050) | (0.504, -0.013, 0.113)→(0.505, -0.013, 0.090) | 0.047→0.035 | 1.00 / 1.000 | 63.316 | 162.565 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.890
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.890
- phase_score: 0.002
- phase_breakdown.align_score: 0.006
- phase_breakdown.approach_score: 0.001
- phase_breakdown.insert_score: 0.001
- phase_breakdown.contact_score: 0.001

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.357
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.890
- **Median Q (composite search score)**: -0.251
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.363


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9cec5bdbb03cce7c3c09816ace5d94f97b8f61fe750542a4a790173a53dc00b4`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `aa1cc88294efeb3bf6fcf727f27d837e44fca2942932baa7feaaed37c752b2f3`; realized-scene SHA-256: `d30c452da2a3cff083d30694df03632a9bb782339e47c14383f7124ad9a32464`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.52962,-0.01705,0.025]},{"name":"target","value":[0.52962,-0.01705,0.025]},{"name":"socket","value":[0.52962,-0.01705,0.025]},{"name":"goal","value":[0.52962,-0.01705,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,-0.01705,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.52962,-0.01705,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.72727,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_above.align_speed":0.06415,"contact_rim.probe_force":7.41103,"contact_rim.probe_retry_x":-0.00468,"contact_rim.probe_retry_y":-0.00607,"descend_to_entry.descend_speed":0.04986,"insert_down.insert_depth":0.0566,"insert_down.insert_force_guard_threshold":33.95656,"insert_down.insert_retry_x":-0.00314,"insert_down.insert_retry_y":-0.00636,"insert_down.insert_speed":0.02472},"optimized_scores":{"best_composite_score":-0.23313,"best_fitness_score":0.35687,"best_task_score":0.88993},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.53622,-0.01725,0.04989],"force_p95":198.21152,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":209.38949,"mean_force":123.68059,"phase_index":4.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.52122,-0.01694,0.04996]}],"total_contact_groups":1},"final_pose_error":0.02764,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.52129,-0.01695,0.04976],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":209.38949,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":345.0,"n_steps_budget":1000.0,"object_pos_end":[0.53012,-0.01488,0.24662],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.16997,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_above","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"align","tcp_end":[0.52308,-0.0149,0.20725],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":678.0,"n_steps_budget":1000.0,"object_pos_end":[0.53601,-0.01684,0.12563],"object_pos_start":[0.53012,-0.01488,0.24662],"object_to_goal_dist_end":0.06052,"object_to_goal_dist_start":0.16997,"object_z_max":0.24662,"peak_contact_force":0.0,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach","tcp_end":[0.52517,-0.01689,0.08713],"tcp_start":[0.52308,-0.0149,0.20725],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.52561,-0.01699,0.10691],"object_pos_start":[0.53601,-0.01684,0.12563],"object_to_goal_dist_end":0.04085,"object_to_goal_dist_start":0.06052,"object_z_max":0.12563,"peak_contact_force":0.0,"phase_name":"contact_rim","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"contact","tcp_end":[0.52514,-0.01698,0.06692],"tcp_start":[0.52517,-0.01689,0.08713],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":339.0,"n_steps_budget":600.0,"object_pos_end":[0.52187,-0.01695,0.11077],"object_pos_start":[0.52561,-0.01699,0.10691],"object_to_goal_dist_end":0.04138,"object_to_goal_dist_start":0.04085,"object_z_max":0.11076,"peak_contact_force":0.0,"phase_name":"lift_off_contact","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.52124,-0.01693,0.07078],"tcp_start":[0.52514,-0.01698,0.06692],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":83.0,"n_steps_budget":1000.0,"object_pos_end":[0.52171,-0.01695,0.08992],"object_pos_start":[0.52187,-0.01695,0.11077],"object_to_goal_dist_end":0.02927,"object_to_goal_dist_start":0.04138,"object_z_max":0.11077,"peak_contact_force":64.0425,"phase_name":"insert_down","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":209.38949,"subtask_id":"insert","tcp_end":[0.52129,-0.01695,0.04976],"tcp_start":[0.52126,-0.01694,0.04982],"tcp_to_object_dist_end":0.04017,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `688a3926bc1208c752fc2d1535fab63bd957243e02b13eac53840dc266efeb6b`; realized-scene SHA-256: `3df42339bb213b8d34da19ed0076dd8b56ad93b79493c43fb7ab2bb6b5f8a158`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.53648,-0.02339,0.025]},{"name":"target","value":[0.53648,-0.02339,0.025]},{"name":"socket","value":[0.53648,-0.02339,0.025]},{"name":"goal","value":[0.53648,-0.02339,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,-0.02339,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53648,-0.02339,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.37441,"average_solve_count":211.0,"average_success_count":211.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_above.align_speed":0.06265,"contact_rim.probe_force":10.87961,"contact_rim.probe_retry_x":0.00277,"contact_rim.probe_retry_y":-0.00585,"descend_to_entry.descend_speed":0.0457,"insert_down.insert_depth":0.044,"insert_down.insert_force_guard_threshold":21.29333,"insert_down.insert_retry_x":0.00038,"insert_down.insert_retry_y":0.00558,"insert_down.insert_speed":0.00756},"optimized_scores":{"best_composite_score":-0.25061,"best_fitness_score":0.33939,"best_task_score":0.84627},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.54373,-0.02362,0.04991],"force_p95":133.93673,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":136.94186,"mean_force":103.92182,"phase_index":4.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.52874,-0.0232,0.05]}],"total_contact_groups":1},"final_pose_error":0.01579,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.52885,-0.02321,0.04983],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":136.94186,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":367.0,"n_steps_budget":1000.0,"object_pos_end":[0.5359,-0.02054,0.24586],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.17094,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_above","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"align","tcp_end":[0.52936,-0.02059,0.2064],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":673.0,"n_steps_budget":1000.0,"object_pos_end":[0.54223,-0.02305,0.12568],"object_pos_start":[0.5359,-0.02054,0.24586],"object_to_goal_dist_end":0.06634,"object_to_goal_dist_start":0.17094,"object_z_max":0.24586,"peak_contact_force":0.0,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach","tcp_end":[0.53197,-0.02315,0.08702],"tcp_start":[0.52936,-0.02059,0.2064],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.53243,-0.02328,0.10676],"object_pos_start":[0.54223,-0.02305,0.12568],"object_to_goal_dist_end":0.04806,"object_to_goal_dist_start":0.06634,"object_z_max":0.12568,"peak_contact_force":0.0,"phase_name":"contact_rim","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"contact","tcp_end":[0.53195,-0.02326,0.06677],"tcp_start":[0.53197,-0.02315,0.08702],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":339.0,"n_steps_budget":600.0,"object_pos_end":[0.52866,-0.02319,0.11048],"object_pos_start":[0.53243,-0.02328,0.10676],"object_to_goal_dist_end":0.04784,"object_to_goal_dist_start":0.04806,"object_z_max":0.11047,"peak_contact_force":0.0,"phase_name":"lift_off_contact","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.52801,-0.02317,0.07049],"tcp_start":[0.53195,-0.02326,0.06677],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":97.0,"n_steps_budget":1000.0,"object_pos_end":[0.52923,-0.02321,0.08995],"object_pos_start":[0.52866,-0.02319,0.11048],"object_to_goal_dist_end":0.03863,"object_to_goal_dist_start":0.04784,"object_z_max":0.11048,"peak_contact_force":67.93302,"phase_name":"insert_down","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":136.94186,"subtask_id":"insert","tcp_end":[0.52885,-0.02321,0.04983],"tcp_start":[0.5288,-0.0232,0.04987],"tcp_to_object_dist_end":0.04013,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a628d07ffd5fd1634a1f36dba43ee92c313515a1a075bf67fe2ba29ce8996148`; realized-scene SHA-256: `025a988ff91962c08fa963a737fe7ec85e866c8c15bf8e1bf01c5bb6961db318`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.47029,-6e-05,0.025]},{"name":"target","value":[0.47029,-6e-05,0.025]},{"name":"socket","value":[0.47029,-6e-05,0.025]},{"name":"goal","value":[0.47029,-6e-05,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.47029,-6e-05,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.47029,-6e-05,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.77128,"average_solve_count":188.0,"average_success_count":188.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_above.align_speed":0.07395,"contact_rim.probe_force":5.53416,"contact_rim.probe_retry_x":0.00242,"contact_rim.probe_retry_y":0.00321,"descend_to_entry.descend_speed":0.0314,"insert_down.insert_depth":0.05572,"insert_down.insert_force_guard_threshold":28.25981,"insert_down.insert_retry_x":-0.0006,"insert_down.insert_retry_y":-0.00445,"insert_down.insert_speed":0.02145},"optimized_scores":{"best_composite_score":-0.25156,"best_fitness_score":0.33844,"best_task_score":0.84382},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.47762,-0.0001,0.04987],"force_p95":136.22667,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":141.36234,"mean_force":96.44716,"phase_index":4.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.46262,-0.00015,0.04989]}],"total_contact_groups":1},"final_pose_error":0.02653,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.47029,-6e-05,0.025],"final_tcp_position":[0.46269,-0.00016,0.0497],"realised_fixture_position":[0.47029,-6e-05,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.47029,-6e-05,0.08]},"peak_contact_force":141.36234,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":293.0,"n_steps_budget":900.0,"object_pos_end":[0.48288,-8e-05,0.24824],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.16911,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_above","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"align","tcp_end":[0.47183,-9e-05,0.2098],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":713.0,"n_steps_budget":1000.0,"object_pos_end":[0.48213,-0.00011,0.12503],"object_pos_start":[0.48288,-8e-05,0.24824],"object_to_goal_dist_end":0.04844,"object_to_goal_dist_start":0.16911,"object_z_max":0.24824,"peak_contact_force":0.0,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach","tcp_end":[0.46655,-0.00013,0.08819],"tcp_start":[0.47183,-9e-05,0.2098],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":238.0,"n_steps_budget":600.0,"object_pos_end":[0.46609,-0.00011,0.11141],"object_pos_start":[0.48213,-0.00011,0.12503],"object_to_goal_dist_end":0.04623,"object_to_goal_dist_start":0.04844,"object_z_max":0.12503,"peak_contact_force":0.0,"phase_name":"contact_rim","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"contact","tcp_end":[0.46549,-0.00011,0.07142],"tcp_start":[0.46655,-0.00013,0.08819],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":339.0,"n_steps_budget":600.0,"object_pos_end":[0.46259,-0.00015,0.11635],"object_pos_start":[0.46609,-0.00011,0.11141],"object_to_goal_dist_end":0.05216,"object_to_goal_dist_start":0.04623,"object_z_max":0.11633,"peak_contact_force":0.0,"phase_name":"lift_off_contact","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.46199,-0.00015,0.07635],"tcp_start":[0.46549,-0.00011,0.07142],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":113.0,"n_steps_budget":1000.0,"object_pos_end":[0.46305,-0.00015,0.08985],"object_pos_start":[0.46259,-0.00015,0.11635],"object_to_goal_dist_end":0.03824,"object_to_goal_dist_start":0.05216,"object_z_max":0.11635,"peak_contact_force":57.97345,"phase_name":"insert_down","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":141.36234,"subtask_id":"insert","tcp_end":[0.46269,-0.00016,0.0497],"tcp_start":[0.46266,-0.00015,0.04975],"tcp_to_object_dist_end":0.04015,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```