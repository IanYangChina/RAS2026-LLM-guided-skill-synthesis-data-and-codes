## Search State

- **Seed**: 6
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → align → insert | arc_cartesian | linear_cartesian | linear_cartesian | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 7 | 0.3258 | 0.82 | ❌ rejected |
| 13 | approach → align → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | 8 | 0.1883 | 0.84 | ❌ rejected |
| 12 | approach → align → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | 8 | 0.4165 | 0.81 | ❌ rejected |
| 11 | approach → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3652 | 0.83 | ❌ rejected |
| 10 | approach → align → insert | arc_cartesian | linear_cartesian | linear_cartesian | impedance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.0436 | 0.82 | ❌ rejected |

**Proposal policy**: task_score is 0.82 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `8fefb664610d091fa81ee0c279409778edf059cbe39fe254365372fa331a0db3`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5030531481177548, -0.012538330414932925, 0.08]
- Frozen socket pose: [0.5030531481177548, -0.012538330414932925, 0.025] (static fixture for this episode)
- Goal object position: (0.5030531481177548, -0.012538330414932925, 0.025)
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
  frozen_task_target: [0.5031, -0.0125, 0.08]
  frozen_socket_position: [0.5031, -0.0125, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5030531481177548, -0.012538330414932925, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5030531481177548, -0.012538330414932925, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 8fefb664610d091fa81ee0c279409778edf059cbe39fe254365372fa331a0db3

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.842, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5030531481177548, -0.012538330414932925, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.5030531481177548, -0.012538330414932925, 0.025) | approach/contact targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.326) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: approach_socket
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: insert_peg
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_above_socket
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.005
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: approach_contact_guard
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.005
  subtask_id: approach_socket
- id: align_lateral
  type: align
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.002
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: channel_axis
      tolerance: 0.02
  parameters:
    lateral_x_offset:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_y_offset:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
  subtask_id: approach_socket
- id: insert_into_hole
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    offset_along_axis:
      distance: 0.055
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: channel_axis
      tolerance: 0.02
  parameters:
    force_threshold:
      type: scalar
      range:
      - 10.0
      - 40.0
      default: 25.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    insert_depth:
      type: scalar
      range:
      - 0.03
      - 0.07
      default: 0.055
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insert_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.003
    - 0.003
    - 0.0
  subtask_id: insert_peg

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above_socket** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.005
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=approach_contact_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.005]
- **align_lateral** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.002
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.02
  - parameter_bindings:
    - lateral_x_offset: status=consumed; consumers=target.offset.x (add)
    - lateral_y_offset: status=consumed; consumers=target.offset.y (add)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.005, 0.005, 0.0]
- **insert_into_hole** (`insert`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], offset_along_axis={axis=channel_axis, distance=0.055, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.02
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - insert_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insert_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.003, 0.003, 0.0]

## Design Metrics

- **Composite score**: 0.326
- **task_score** (E): 0.821
- **fitness_score**: 0.372  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_above_socket | 0.00 | 0.0015 |
| align_lateral | 0.00 | 0.0683 |
| insert_into_hole | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_above_socket | approach | 0.00 / guard_failure | (0.443, 0.004, 0.092)→(0.441, 0.004, 0.092) | (0.504, -0.000, 0.340)→(0.483, 0.004, 0.104) | 0.260→0.031 |
| align_lateral | align | 0.00 / step_budget | (0.441, 0.004, 0.092)→(0.443, 0.010, 0.159) | (0.480, 0.004, 0.103)→(0.481, 0.010, 0.148) | 0.032→0.074 |
| insert_into_hole | insert | 1.00 / force_exceeded | (0.443, 0.010, 0.159)→(0.443, 0.010, 0.159) | (0.481, 0.010, 0.148)→(0.481, 0.010, 0.148) | 0.074→0.073 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.833
- alignment_error: None
- terminal_score: 0.833
- phase_score: 0.076
- phase_breakdown.approach_socket_score: 0.252
- phase_breakdown.insert_peg_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.379
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.833
- **Median Q (composite search score)**: 0.326
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.355


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `60385b1f31aca3065ea31945cfeaa028cd4432c7d54684f37d7ce3abfb247b97`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `4bee8669cc79b9d5e3314636941bfd5dcacadb9648a0bfff5f763dbb49e79a76`; realized-scene SHA-256: `8fefb664610d091fa81ee0c279409778edf059cbe39fe254365372fa331a0db3`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.50305,-0.01254,0.025]},{"name":"target","value":[0.50305,-0.01254,0.025]},{"name":"socket","value":[0.50305,-0.01254,0.025]},{"name":"goal","value":[0.50305,-0.01254,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,-0.01254,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.50305,-0.01254,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.12245,"average_solve_count":49.0,"average_success_count":49.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_lateral.lateral_x_offset":0.00997,"align_lateral.lateral_y_offset":-0.00519,"approach_above_socket.approach_speed":0.06624,"approach_above_socket.arc_height":0.09774,"insert_into_hole.force_threshold":13.35894,"insert_into_hole.insert_depth":0.16048,"insert_into_hole.insert_speed":0.02927},"optimized_scores":{"best_composite_score":0.33202,"best_fitness_score":0.37868,"best_task_score":0.83307},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54821,-0.0097,0.07885],"force_p95":1046.58642,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1055.73829,"mean_force":964.2196,"phase_index":0.0,"phase_name":"approach_above_socket","phase_type":"approach","tcp_position_centroid":[0.44875,-0.0057,0.09127]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.45478,-0.00573,0.07875],"force_p95":843.44132,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":937.15702,"mean_force":312.38567,"phase_index":0.0,"phase_name":"approach_above_socket","phase_type":"approach","tcp_position_centroid":[0.44998,-0.00569,0.0917]},{"body_a":"peg_socket","body_b":"link7","contact_count":995.0,"contact_point_centroid":[0.56207,-0.00721,0.07985],"force_p95":333.1756,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":721.11819,"mean_force":223.37098,"phase_index":1.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.45235,-0.01027,0.16217]},{"body_a":"peg_socket","body_b":"link6","contact_count":553.0,"contact_point_centroid":[0.56298,-0.01061,0.07946],"force_p95":344.54344,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":557.5779,"mean_force":249.02532,"phase_index":1.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.4442,-0.01232,0.15849]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.56299,-0.00934,0.07999],"force_p95":335.22129,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":335.22129,"mean_force":335.22129,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.43916,-0.01639,0.15056]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.56221,-0.01562,0.07996],"force_p95":165.85966,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":165.85966,"mean_force":165.85966,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.43916,-0.01639,0.15056]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.44856,-0.00582,0.07891],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.44469,-0.00576,0.09231]}],"total_contact_groups":7},"final_pose_error":0.23972,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.43915,-0.01636,0.15054],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"phases":[{"n_steps":93.0,"n_steps_budget":600.0,"object_pos_end":[0.48767,-0.00584,0.10429],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.02786,"object_to_goal_dist_start":0.26034,"object_z_max":0.34445,"phase_name":"approach_above_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_socket","tcp_end":[0.4462,-0.00573,0.09114],"tcp_start":[0.44773,-0.00571,0.09105],"tcp_to_object_dist_end":0.0435,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47827,-0.01487,0.14235],"object_pos_start":[0.48454,-0.00587,0.10253],"object_to_goal_dist_end":0.06768,"object_to_goal_dist_start":0.02795,"object_z_max":0.16189,"phase_name":"align_lateral","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"approach_socket","tcp_end":[0.43916,-0.01639,0.15056],"tcp_start":[0.4462,-0.00573,0.09114],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.47827,-0.01485,0.14234],"object_pos_start":[0.47827,-0.01487,0.14235],"object_to_goal_dist_end":0.06766,"object_to_goal_dist_start":0.06768,"object_z_max":0.14235,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","subtask_id":"insert_peg","tcp_end":[0.43915,-0.01636,0.15054],"tcp_start":[0.43916,-0.01639,0.15056],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `b372e597e9ea71ad79503f48aaa87b3bb2c0c3a8e8252ca19ea88229597605ec`; realized-scene SHA-256: `f2535c6a7dfc5a3ca3c25224b40d7fd8d1111b06ec904a3c56a54673c2686a85`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.51001,0.03178,0.025]},{"name":"target","value":[0.51001,0.03178,0.025]},{"name":"socket","value":[0.51001,0.03178,0.025]},{"name":"goal","value":[0.51001,0.03178,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.03178,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.51001,0.03178,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.12245,"average_solve_count":49.0,"average_success_count":49.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_lateral.lateral_x_offset":0.00239,"align_lateral.lateral_y_offset":-0.00394,"approach_above_socket.approach_speed":0.03253,"approach_above_socket.arc_height":0.07343,"insert_into_hole.force_threshold":18.04694,"insert_into_hole.insert_depth":0.13642,"insert_into_hole.insert_speed":0.03583},"optimized_scores":{"best_composite_score":0.32644,"best_fitness_score":0.3731,"best_task_score":0.82219},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.53625,0.00141,0.07764],"force_p95":1122.55705,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1238.73082,"mean_force":186.43752,"phase_index":1.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.44061,0.01122,0.10998]},{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.5444,0.00829,0.07812],"force_p95":1063.80326,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1074.14697,"mean_force":933.81409,"phase_index":0.0,"phase_name":"approach_above_socket","phase_type":"approach","tcp_position_centroid":[0.44531,0.01042,0.09259]},{"body_a":"peg_socket","body_b":"link7","contact_count":918.0,"contact_point_centroid":[0.56866,0.02071,0.07985],"force_p95":421.33219,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1068.24188,"mean_force":244.61285,"phase_index":1.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.44963,0.01928,0.15391]},{"body_a":"peg_socket","body_b":"link6","contact_count":876.0,"contact_point_centroid":[0.56986,0.01535,0.07953],"force_p95":514.42841,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":742.03121,"mean_force":325.90542,"phase_index":1.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.45056,0.0197,0.1562]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5392,0.00162,0.07893],"force_p95":307.28131,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":307.28131,"mean_force":307.28131,"phase_index":0.0,"phase_name":"approach_above_socket","phase_type":"approach","tcp_position_centroid":[0.44323,0.01044,0.09225]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.56993,0.01877,0.07998],"force_p95":202.0404,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":202.0404,"mean_force":202.0404,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.4422,0.02921,0.14294]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.56932,0.02407,0.07996],"force_p95":152.31814,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":152.31814,"mean_force":152.31814,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.4422,0.02921,0.14294]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.45086,0.01047,0.07931],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_above_socket","phase_type":"approach","tcp_position_centroid":[0.44531,0.01042,0.09259]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.4501,0.01047,0.07963],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.44183,0.01044,0.0926]}],"total_contact_groups":9},"final_pose_error":0.21063,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.44218,0.02922,0.14298],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"phases":[{"n_steps":95.0,"n_steps_budget":780.0,"object_pos_end":[0.48345,0.01069,0.10379],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.03089,"object_to_goal_dist_start":0.26034,"object_z_max":0.3444,"phase_name":"approach_above_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_socket","tcp_end":[0.44183,0.01044,0.0926],"tcp_start":[0.44323,0.01044,0.09225],"tcp_to_object_dist_end":0.0431,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48171,0.02675,0.13717],"object_pos_start":[0.48056,0.01073,0.10261],"object_to_goal_dist_end":0.06571,"object_to_goal_dist_start":0.0317,"object_z_max":0.16764,"phase_name":"align_lateral","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"approach_socket","tcp_end":[0.4422,0.02921,0.14294],"tcp_start":[0.44183,0.01044,0.0926],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.48169,0.02675,0.1372],"object_pos_start":[0.48171,0.02675,0.13717],"object_to_goal_dist_end":0.06574,"object_to_goal_dist_start":0.06571,"object_z_max":0.13717,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","subtask_id":"insert_peg","tcp_end":[0.44218,0.02922,0.14298],"tcp_start":[0.4422,0.02921,0.14294],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ae45bae888bf338225755528d96cf0281f13a4171bef9e43a6d9a98635b19bee`; realized-scene SHA-256: `586a2957baaedcadf28af0fbf7d32a1a4534953c544a60ba5a7051ee138050bc`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.48616,0.03898,0.025]},{"name":"target","value":[0.48616,0.03898,0.025]},{"name":"socket","value":[0.48616,0.03898,0.025]},{"name":"goal","value":[0.48616,0.03898,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.03898,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.48616,0.03898,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.10204,"average_solve_count":49.0,"average_success_count":49.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_lateral.lateral_x_offset":-0.00774,"align_lateral.lateral_y_offset":-0.00979,"approach_above_socket.approach_speed":0.0253,"approach_above_socket.arc_height":0.09961,"insert_into_hole.force_threshold":19.6308,"insert_into_hole.insert_depth":0.11899,"insert_into_hole.insert_speed":0.0083},"optimized_scores":{"best_composite_score":0.3189,"best_fitness_score":0.36556,"best_task_score":0.80779},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.53833,0.00586,0.07869],"force_p95":1050.59895,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1059.6459,"mean_force":942.32236,"phase_index":0.0,"phase_name":"approach_above_socket","phase_type":"approach","tcp_position_centroid":[0.43913,0.00824,0.09304]},{"body_a":"peg_socket","body_b":"link7","contact_count":852.0,"contact_point_centroid":[0.54541,0.01816,0.07985],"force_p95":346.78572,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":684.2988,"mean_force":236.81952,"phase_index":1.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.46383,0.01419,0.18994]},{"body_a":"peg_socket","body_b":"link6","contact_count":591.0,"contact_point_centroid":[0.54608,0.01489,0.07923],"force_p95":348.33363,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":411.88552,"mean_force":296.24362,"phase_index":1.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.46357,0.0161,0.19537]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.54612,0.01582,0.07942],"force_p95":257.18831,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":257.18831,"mean_force":257.18831,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.44685,0.01781,0.18213]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54533,0.02057,0.07995],"force_p95":77.15964,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":77.15964,"mean_force":77.15964,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.44685,0.01781,0.18213]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.4435,0.00827,0.07935],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_above_socket","phase_type":"approach","tcp_position_centroid":[0.43913,0.00824,0.09304]},{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.43878,0.00838,0.07942],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.43506,0.00826,0.09338]}],"total_contact_groups":7},"final_pose_error":0.22553,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.4468,0.0177,0.18207],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"phases":[{"n_steps":94.0,"n_steps_budget":1000.0,"object_pos_end":[0.47719,0.00845,0.10451],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.03453,"object_to_goal_dist_start":0.26034,"object_z_max":0.34405,"phase_name":"approach_above_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_socket","tcp_end":[0.43558,0.00826,0.09301],"tcp_start":[0.43701,0.00826,0.09269],"tcp_to_object_dist_end":0.04318,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48218,0.01808,0.16336],"object_pos_start":[0.47423,0.00849,0.10328],"object_to_goal_dist_end":0.08714,"object_to_goal_dist_start":0.03575,"object_z_max":0.17588,"phase_name":"align_lateral","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"approach_socket","tcp_end":[0.44685,0.01781,0.18213],"tcp_start":[0.43558,0.00826,0.09301],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.48213,0.018,0.16332],"object_pos_start":[0.48218,0.01808,0.16336],"object_to_goal_dist_end":0.08709,"object_to_goal_dist_start":0.08714,"object_z_max":0.16336,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","subtask_id":"insert_peg","tcp_end":[0.4468,0.0177,0.18207],"tcp_start":[0.44685,0.01781,0.18213],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```