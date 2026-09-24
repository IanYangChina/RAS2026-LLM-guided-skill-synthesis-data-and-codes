## Search State

- **Seed**: 4
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → align → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | 7 | 0.1362 | 0.90 | ❌ rejected |
| 3 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.1391 | 0.96 | ❌ rejected |
| 2 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.1391 | 0.96 | ❌ rejected |
| 1 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.1391 | 0.96 | ❌ rejected |
| 0 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.1391 | 0.96 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.90). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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
- Frozen realised-scene SHA-256: `6aa6006ba5d7c7f83773c59f42ad1597db3f9073c3225635eb35deca1cb0f02a`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5354444884457887, 0.000906204225148928, 0.08]
- Frozen socket pose: [0.5354444884457887, 0.000906204225148928, 0.025] (static fixture for this episode)
- Goal object position: (0.5354444884457887, 0.000906204225148928, 0.025)
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
  frozen_task_target: [0.5354, 0.0009, 0.08]
  frozen_socket_position: [0.5354, 0.0009, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5354444884457887, 0.000906204225148928, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5354444884457887, 0.000906204225148928, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 6aa6006ba5d7c7f83773c59f42ad1597db3f9073c3225635eb35deca1cb0f02a

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.962, which indicates the subtask decomposition is already effective.
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
| `goal` | offset from task goal position (0.5354444884457887, 0.000906204225148928, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.5354444884457887, 0.000906204225148928, 0.025) | approach/contact targets near fixture |

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

## Current Skill (Q=0.136) — your mutation base

```yaml
skill: peg_insert
skill_type: arm_gripper
phases:
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: release_1
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
- id: insert_1
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: force_exceeded
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.15
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0

```

## Design Metrics

- **Composite score**: 0.136
- **task_score** (E): 0.902
- **fitness_score**: 0.546  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| push_1 | 1.00 | 0.2253 |
| align_1 | 0.67 | 0.0117 |
| release_1 | 0.00 | 0.0002 |
| insert_1 | 0.00 | 0.0138 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| push_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, 0.004, 0.077) | (0.504, -0.000, 0.340)→(0.528, 0.004, 0.115) | 0.260→0.048 |
| align_1 | align | 0.67 / step_budget | (0.516, 0.004, 0.077)→(0.516, 0.004, 0.088) | (0.528, 0.004, 0.115)→(0.536, 0.007, 0.110) | 0.048→0.049 |
| release_1 | descend | 0.00 / step_budget | (0.516, 0.004, 0.088)→(0.516, 0.004, 0.088) | (0.536, 0.007, 0.110)→(0.536, 0.007, 0.110) | 0.049→0.049 |
| insert_1 | insert | 0.00 / guard_failure | (0.516, 0.004, 0.088)→(0.527, 0.006, 0.082) | (0.536, 0.007, 0.110)→(0.548, 0.008, 0.104) | 0.049→0.056 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.966
- alignment_error: None
- terminal_score: 0.966
- phase_score: 0.310
- phase_breakdown.approach_entry_score: 0.787
- phase_breakdown.insertion_goal_score: 0.105

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.572
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.966
- **Median Q (composite search score)**: 0.123
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.316


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `1c06d48834291abac995c6cc1d2cd84f840e8dd85a042a042b29bb3e8b43f340`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a5dd99a2832e295b96a2d483dc6e44525a65c5240d3c756ec4d63dfbfe5237b3`; realized-scene SHA-256: `6aa6006ba5d7c7f83773c59f42ad1597db3f9073c3225635eb35deca1cb0f02a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.53544,0.00091,0.025]},{"name":"target","value":[0.53544,0.00091,0.025]},{"name":"socket","value":[0.53544,0.00091,0.025]},{"name":"goal","value":[0.53544,0.00091,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.00091,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53544,0.00091,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":57.0,"average_failure_rate":0.32022,"average_mean_iterations":66.61236,"average_solve_count":178.0,"average_success_count":121.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00126,"align_1.lateral_offset_y":-0.01499,"insert_1.insertion_depth":0.04338,"insert_1.insertion_force":13.12904,"push_1.push_distance":0.04828,"push_1.push_speed":0.02199,"release_1.descend_force_threshold":14.18786},"optimized_scores":{"best_composite_score":0.12327,"best_fitness_score":0.53327,"best_task_score":0.87131},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.56558,0.00246,0.07996],"force_p95":1224.53204,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1224.53204,"mean_force":1224.53204,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.54565,0.00312,0.06556]}],"total_contact_groups":1},"final_pose_error":0.08407,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.54742,0.00335,0.0648],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"phases":[{"n_steps":810.0,"n_steps_budget":1000.0,"object_pos_end":[0.54017,0.00077,0.11298],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.05198,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_entry","tcp_end":[0.52943,0.00077,0.07445],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":0.0,"n_steps_budget":600.0,"object_pos_end":[0.54017,0.00077,0.11298],"object_pos_start":[0.54017,0.00077,0.11298],"object_to_goal_dist_end":0.05198,"object_to_goal_dist_start":0.05198,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"approach_entry","tcp_end":[0.52943,0.00077,0.07445],"tcp_start":[0.52943,0.00077,0.07445],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":0.0,"n_steps_budget":600.0,"object_pos_end":[0.54017,0.00077,0.11298],"object_pos_start":[0.54017,0.00077,0.11298],"object_to_goal_dist_end":0.05198,"object_to_goal_dist_start":0.05198,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"insertion_goal","tcp_end":[0.52943,0.00077,0.07445],"tcp_start":[0.52943,0.00077,0.07445],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":14.0,"n_steps_budget":600.0,"object_pos_end":[0.55933,0.00197,0.10296],"object_pos_start":[0.54017,0.00077,0.11298],"object_to_goal_dist_end":0.06365,"object_to_goal_dist_start":0.05198,"object_z_max":0.11298,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","subtask_id":"insertion_goal","tcp_end":[0.54742,0.00335,0.0648],"tcp_start":[0.52943,0.00077,0.07445],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `82356f74d11e1888d903e80aabfa97b50f0a1f9374ab8997097863e47a04dcc6`; realized-scene SHA-256: `68ad8ffad13ff17e4e79d7c12ed07a79b854360d1380b55b4d752be6df0d8737`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.5244,0.02464,0.025]},{"name":"target","value":[0.5244,0.02464,0.025]},{"name":"socket","value":[0.5244,0.02464,0.025]},{"name":"goal","value":[0.5244,0.02464,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.02464,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.5244,0.02464,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":60.0,"average_failure_rate":0.37037,"average_mean_iterations":76.58025,"average_solve_count":162.0,"average_success_count":102.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.01464,"align_1.lateral_offset_y":-0.00044,"insert_1.insertion_depth":0.04835,"insert_1.insertion_force":17.19184,"push_1.push_distance":0.04929,"push_1.push_speed":0.04766,"release_1.descend_force_threshold":15.12172},"optimized_scores":{"best_composite_score":0.12301,"best_fitness_score":0.53301,"best_task_score":0.8698},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.55505,0.024,0.07978],"force_p95":1229.52679,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1229.52679,"mean_force":1229.52679,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.53507,0.0239,0.06498]}],"total_contact_groups":1},"final_pose_error":0.08846,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.5368,0.02432,0.06424],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"phases":[{"n_steps":801.0,"n_steps_budget":1000.0,"object_pos_end":[0.53063,0.02297,0.11207],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.04994,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_entry","tcp_end":[0.51902,0.02301,0.07379],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":0.0,"n_steps_budget":600.0,"object_pos_end":[0.53063,0.02297,0.11207],"object_pos_start":[0.53063,0.02297,0.11207],"object_to_goal_dist_end":0.04994,"object_to_goal_dist_start":0.04994,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"approach_entry","tcp_end":[0.51902,0.02301,0.07379],"tcp_start":[0.51902,0.02301,0.07379],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":0.0,"n_steps_budget":600.0,"object_pos_end":[0.53063,0.02297,0.11207],"object_pos_start":[0.53063,0.02297,0.11207],"object_to_goal_dist_end":0.04994,"object_to_goal_dist_start":0.04994,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"insertion_goal","tcp_end":[0.51902,0.02301,0.07379],"tcp_start":[0.51902,0.02301,0.07379],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":14.0,"n_steps_budget":630.0,"object_pos_end":[0.54959,0.0245,0.10214],"object_pos_start":[0.53063,0.02297,0.11207],"object_to_goal_dist_end":0.05958,"object_to_goal_dist_start":0.04994,"object_z_max":0.11207,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","subtask_id":"insertion_goal","tcp_end":[0.5368,0.02432,0.06424],"tcp_start":[0.51902,0.02301,0.07379],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `4fedbe547233117d2a5522e0e6da389f32d172824e1a5c898bb2e8c1e5f99b78`; realized-scene SHA-256: `8fefb664610d091fa81ee0c279409778edf059cbe39fe254365372fa331a0db3`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.50305,-0.01254,0.025]},{"name":"target","value":[0.50305,-0.01254,0.025]},{"name":"socket","value":[0.50305,-0.01254,0.025]},{"name":"goal","value":[0.50305,-0.01254,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,-0.01254,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.50305,-0.01254,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":8.0,"average_failure_rate":0.06504,"average_mean_iterations":17.39024,"average_solve_count":123.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00271,"align_1.lateral_offset_y":0.00413,"insert_1.insertion_depth":0.04538,"insert_1.insertion_force":19.7963,"push_1.push_distance":0.04226,"push_1.push_speed":0.04599,"release_1.descend_force_threshold":10.41999},"optimized_scores":{"best_composite_score":0.16228,"best_fitness_score":0.57228,"best_task_score":0.96615},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":70.0,"contact_point_centroid":[0.54812,0.00557,0.07965],"force_p95":4524.72404,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5614.34491,"mean_force":846.8766,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51678,-0.00472,0.09637]},{"body_a":"attachment","body_b":"peg_socket","contact_count":12.0,"contact_point_centroid":[0.52106,0.01919,0.07818],"force_p95":5312.55252,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5429.33995,"mean_force":3011.21073,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51865,0.00572,0.07356]},{"body_a":"peg_socket","body_b":"link7","contact_count":154.0,"contact_point_centroid":[0.56276,0.04129,0.07821],"force_p95":666.45623,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":922.46239,"mean_force":432.32994,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5062,-0.01248,0.11342]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.56304,0.02201,0.07133],"force_p95":551.44071,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":551.44071,"mean_force":551.44071,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49822,-0.0109,0.11711]}],"total_contact_groups":4},"final_pose_error":0.13796,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.49824,-0.0105,0.11748],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"phases":[{"n_steps":751.0,"n_steps_budget":1000.0,"object_pos_end":[0.51213,-0.0118,0.11943],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.04291,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_entry","tcp_end":[0.499,-0.01178,0.08165],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":283.0,"n_steps_budget":600.0,"object_pos_end":[0.53581,-0.00339,0.10565],"object_pos_start":[0.51213,-0.0118,0.11943],"object_to_goal_dist_end":0.04418,"object_to_goal_dist_start":0.04291,"object_z_max":0.12169,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"approach_entry","tcp_end":[0.49822,-0.01139,0.11672],"tcp_start":[0.499,-0.01178,0.08165],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.5358,-0.00294,0.10597],"object_pos_start":[0.53581,-0.00339,0.10565],"object_to_goal_dist_end":0.04433,"object_to_goal_dist_start":0.04418,"object_z_max":0.10565,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"insertion_goal","tcp_end":[0.49822,-0.0109,0.11711],"tcp_start":[0.49822,-0.01139,0.11672],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":1.0,"n_steps_budget":870.0,"object_pos_end":[0.53581,-0.00256,0.10629],"object_pos_start":[0.5358,-0.00294,0.10597],"object_to_goal_dist_end":0.0445,"object_to_goal_dist_start":0.04433,"object_z_max":0.10597,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","subtask_id":"insertion_goal","tcp_end":[0.49824,-0.0105,0.11748],"tcp_start":[0.49822,-0.0109,0.11711],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```