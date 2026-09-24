## Search State

- **Seed**: 6
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.0910 | 0.84 | ✅ accepted |
| 1 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0178 | 0.77 | ✅ accepted |
| 0 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0178 | 0.77 | ✅ accepted |

**Proposal policy**: task_score is 0.84 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.835, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.091) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: approach_socket
  offset:
  - 0.0
  - 0.0
  - 0.04
  weight: 0.3
- id: insert_peg
  offset:
  - 0.0
  - 0.0
  - -0.06
  weight: 0.7
phases:
- id: approach_above_socket
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.06
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
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
  subtask_id: approach_socket
- id: align_lateral
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.06
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
    - 0.06
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
      - 5.0
      - 35.0
      default: 20
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
  guards:
  - id: lateral_force_guard
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
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
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.06], tolerance=0.005
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **align_lateral** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.06], tolerance=0.002
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.02
  - parameter_bindings:
    - lateral_x_offset: status=consumed; consumers=target.offset.x (add)
    - lateral_y_offset: status=consumed; consumers=target.offset.y (add)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.005, 0.005, 0.0]
- **insert_into_hole** (`insert`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.06], offset_along_axis={axis=channel_axis, distance=0.055, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.02
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - insert_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insert_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lateral_force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.003, 0.003, 0.0]

## Design Metrics

- **Composite score**: 0.091
- **task_score** (E): 0.835
- **fitness_score**: 0.421  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_above_socket | 0.33 | 0.1541 |
| align_lateral | 0.33 | 0.0363 |
| insert_into_hole | 0.00 | 0.0003 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_above_socket | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.457, 0.004, 0.153) | (0.504, -0.000, 0.340)→(0.495, 0.005, 0.143) | 0.260→0.064 |
| align_lateral | align | 0.33 / step_budget | (0.457, 0.004, 0.153)→(0.482, -0.002, 0.167) | (0.495, 0.005, 0.143)→(0.516, 0.003, 0.150) | 0.064→0.074 |
| insert_into_hole | insert | 0.00 / guard_failure | (0.482, -0.002, 0.167)→(0.482, -0.002, 0.167) | (0.516, 0.003, 0.150)→(0.516, 0.003, 0.150) | 0.074→0.074 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.840
- alignment_error: None
- terminal_score: 0.840
- phase_score: 0.221
- phase_breakdown.approach_socket_score: 0.531
- phase_breakdown.insert_peg_score: 0.088

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.469
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.840
- **Median Q (composite search score)**: 0.077
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.390


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.05,"average_solve_count":60.0,"average_success_count":60.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_lateral.lateral_x_offset":-0.00972,"align_lateral.lateral_y_offset":-0.00886,"approach_above_socket.approach_speed":0.03946,"insert_into_hole.force_threshold":23.15939,"insert_into_hole.insert_depth":0.04361,"insert_into_hole.insert_speed":0.02769},"optimized_scores":{"best_composite_score":0.05753,"best_fitness_score":0.38753,"best_task_score":0.83186},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":503.0,"contact_point_centroid":[0.56297,-0.00311,0.0793],"force_p95":642.14162,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1388.7444,"mean_force":267.25656,"phase_index":0.0,"phase_name":"approach_above_socket","phase_type":"approach","tcp_position_centroid":[0.44631,-0.00199,0.16176]},{"body_a":"peg_socket","body_b":"link7","contact_count":900.0,"contact_point_centroid":[0.56167,0.00252,0.07987],"force_p95":379.70365,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1300.69806,"mean_force":227.86743,"phase_index":0.0,"phase_name":"approach_above_socket","phase_type":"approach","tcp_position_centroid":[0.44762,-0.00165,0.15882]},{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.45093,-0.00078,0.07909],"force_p95":986.40426,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1034.10508,"mean_force":196.22083,"phase_index":0.0,"phase_name":"approach_above_socket","phase_type":"approach","tcp_position_centroid":[0.44658,-0.00074,0.09252]},{"body_a":"peg_socket","body_b":"link6","contact_count":571.0,"contact_point_centroid":[0.56285,-0.00389,0.07927],"force_p95":626.00551,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":749.87779,"mean_force":385.08772,"phase_index":1.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.45096,-0.0037,0.16727]},{"body_a":"peg_socket","body_b":"link7","contact_count":571.0,"contact_point_centroid":[0.5619,-0.00159,0.07995],"force_p95":475.34072,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":575.71911,"mean_force":269.27211,"phase_index":1.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.45096,-0.0037,0.16727]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.56284,-0.00461,0.07934],"force_p95":385.94247,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":386.2456,"mean_force":352.64118,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.46895,-0.00581,0.18715]},{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.56187,-0.00796,0.07997],"force_p95":228.3899,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":233.59934,"mean_force":192.22538,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.46895,-0.00581,0.18715]}],"total_contact_groups":7},"final_pose_error":0.09723,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.46905,-0.00558,0.18721],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48175,-0.00235,0.14682],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.06931,"object_to_goal_dist_start":0.26034,"object_z_max":0.34438,"phase_name":"approach_above_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_socket","tcp_end":[0.44312,-0.00251,0.15717],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.50319,-0.00626,0.16652],"object_pos_start":[0.48175,-0.00235,0.14682],"object_to_goal_dist_end":0.08681,"object_to_goal_dist_start":0.06931,"object_z_max":0.1665,"phase_name":"align_lateral","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"approach_socket","tcp_end":[0.4689,-0.00592,0.18711],"tcp_start":[0.44312,-0.00251,0.15717],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50324,-0.00618,0.16655],"object_pos_start":[0.50319,-0.00626,0.16652],"object_to_goal_dist_end":0.08683,"object_to_goal_dist_start":0.08681,"object_z_max":0.16657,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","subtask_id":"insert_peg","tcp_end":[0.46905,-0.00558,0.18721],"tcp_start":[0.46901,-0.0057,0.18718],"tcp_to_object_dist_end":0.03995,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.08475,"average_solve_count":59.0,"average_success_count":59.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_lateral.lateral_x_offset":0.00863,"align_lateral.lateral_y_offset":-0.00867,"approach_above_socket.approach_speed":0.05905,"insert_into_hole.force_threshold":11.90681,"insert_into_hole.insert_depth":0.05755,"insert_into_hole.insert_speed":0.02775},"optimized_scores":{"best_composite_score":0.07693,"best_fitness_score":0.40693,"best_task_score":0.8341},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.45272,0.00144,0.07916],"force_p95":988.27488,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1035.68565,"mean_force":196.6014,"phase_index":0.0,"phase_name":"approach_above_socket","phase_type":"approach","tcp_position_centroid":[0.44758,0.00143,0.09243]},{"body_a":"peg_socket","body_b":"link7","contact_count":900.0,"contact_point_centroid":[0.568,0.00955,0.07984],"force_p95":486.6231,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":934.04352,"mean_force":260.54345,"phase_index":0.0,"phase_name":"approach_above_socket","phase_type":"approach","tcp_position_centroid":[0.44847,0.00573,0.14912]},{"body_a":"peg_socket","body_b":"link6","contact_count":604.0,"contact_point_centroid":[0.56985,0.00504,0.07936],"force_p95":539.56018,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":880.17542,"mean_force":337.50409,"phase_index":0.0,"phase_name":"approach_above_socket","phase_type":"approach","tcp_position_centroid":[0.44689,0.00693,0.15187]},{"body_a":"peg_socket","body_b":"link7","contact_count":410.0,"contact_point_centroid":[0.56872,0.01296,0.07992],"force_p95":664.72788,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":850.73971,"mean_force":376.7618,"phase_index":1.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.45825,0.00829,0.16783]},{"body_a":"peg_socket","body_b":"link6","contact_count":531.0,"contact_point_centroid":[0.56977,0.00874,0.07946],"force_p95":737.39168,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":805.23367,"mean_force":425.33025,"phase_index":1.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.46237,0.00953,0.17396]},{"body_a":"peg_socket","body_b":"link7","contact_count":26.0,"contact_point_centroid":[0.53916,-0.00179,0.07905],"force_p95":585.58012,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":643.34505,"mean_force":358.07128,"phase_index":0.0,"phase_name":"approach_above_socket","phase_type":"approach","tcp_position_centroid":[0.44571,0.00156,0.10275]},{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.56983,0.02407,0.07969],"force_p95":523.01224,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":527.3647,"mean_force":481.97313,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.49083,0.02064,0.17473]}],"total_contact_groups":7},"final_pose_error":0.09388,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.49126,0.02045,0.17375],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49267,0.00855,0.15154],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.07242,"object_to_goal_dist_start":0.26034,"object_z_max":0.34438,"phase_name":"approach_above_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_socket","tcp_end":[0.45471,0.00855,0.16416],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.52533,0.02081,0.15532],"object_pos_start":[0.49267,0.00855,0.15154],"object_to_goal_dist_end":0.08215,"object_to_goal_dist_start":0.07242,"object_z_max":0.17501,"phase_name":"align_lateral","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"approach_socket","tcp_end":[0.49065,0.02067,0.17526],"tcp_start":[0.45471,0.00855,0.16416],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.52556,0.02079,0.15493],"object_pos_start":[0.52533,0.02081,0.15532],"object_to_goal_dist_end":0.08185,"object_to_goal_dist_start":0.08215,"object_z_max":0.15532,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","subtask_id":"insert_peg","tcp_end":[0.49126,0.02045,0.17375],"tcp_start":[0.49103,0.02058,0.17421],"tcp_to_object_dist_end":0.03912,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.2069,"average_solve_count":58.0,"average_success_count":58.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_lateral.lateral_x_offset":-0.00184,"align_lateral.lateral_y_offset":0.0087,"approach_above_socket.approach_speed":0.09875,"insert_into_hole.force_threshold":10.40886,"insert_into_hole.insert_depth":0.03029,"insert_into_hole.insert_speed":0.01729},"optimized_scores":{"best_composite_score":0.13858,"best_fitness_score":0.46858,"best_task_score":0.83983},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.45184,0.00468,0.07887],"force_p95":3162.13945,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3572.03749,"mean_force":574.93445,"phase_index":0.0,"phase_name":"approach_above_socket","phase_type":"approach","tcp_position_centroid":[0.44781,0.00302,0.09163]},{"body_a":"attachment","body_b":"peg_socket","contact_count":12.0,"contact_point_centroid":[0.45751,0.00301,0.079],"force_p95":2656.36745,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2976.9051,"mean_force":691.83289,"phase_index":0.0,"phase_name":"approach_above_socket","phase_type":"approach","tcp_position_centroid":[0.44982,0.00304,0.09134]},{"body_a":"peg_socket","body_b":"link7","contact_count":900.0,"contact_point_centroid":[0.546,0.00953,0.07988],"force_p95":300.62993,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":841.91893,"mean_force":285.28869,"phase_index":0.0,"phase_name":"approach_above_socket","phase_type":"approach","tcp_position_centroid":[0.46688,0.00341,0.13047]},{"body_a":"peg_socket","body_b":"link7","contact_count":571.0,"contact_point_centroid":[0.54606,0.02636,0.07996],"force_p95":316.85123,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":318.97603,"mean_force":294.52384,"phase_index":1.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.47495,-0.00597,0.13725]},{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54606,0.0333,0.07996],"force_p95":291.80227,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":292.08184,"mean_force":289.55356,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.48555,-0.02088,0.13887]}],"total_contact_groups":5},"final_pose_error":0.06694,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.48584,-0.02134,0.13872],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"phases":[{"n_steps":992.0,"n_steps_budget":1000.0,"object_pos_end":[0.51031,0.00978,0.1293],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.0513,"object_to_goal_dist_start":0.26034,"object_z_max":0.34438,"phase_name":"approach_above_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_socket","tcp_end":[0.4717,0.00574,0.13892],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.52052,-0.00458,0.12851],"object_pos_start":[0.51031,0.00978,0.1293],"object_to_goal_dist_end":0.05287,"object_to_goal_dist_start":0.0513,"object_z_max":0.12947,"phase_name":"align_lateral","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"approach_socket","tcp_end":[0.48545,-0.02073,0.13892],"tcp_start":[0.4717,0.00574,0.13892],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.52059,-0.00464,0.12848],"object_pos_start":[0.52052,-0.00458,0.12851],"object_to_goal_dist_end":0.05287,"object_to_goal_dist_start":0.05287,"object_z_max":0.12851,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","subtask_id":"insert_peg","tcp_end":[0.48584,-0.02134,0.13872],"tcp_start":[0.48567,-0.02106,0.13882],"tcp_to_object_dist_end":0.03989,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```