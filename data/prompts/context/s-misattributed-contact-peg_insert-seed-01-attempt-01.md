## Search State

- **Seed**: 1
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → align → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.2679 | 0.84 | ❌ rejected |
| 0 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.7475 | 0.96 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `ad40e378f39a19b149b009dee38b90e3211daf0cadc26f2bf0cba9c113417c3b`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5009457299760202, 0.03603709570607482, 0.08]
- Frozen socket pose: [0.5009457299760202, 0.03603709570607482, 0.025] (static fixture for this episode)
- Goal object position: (0.5009457299760202, 0.03603709570607482, 0.025)
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
  frozen_task_target: [0.5009, 0.036, 0.08]
  frozen_socket_position: [0.5009, 0.036, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5009457299760202, 0.03603709570607482, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5009457299760202, 0.03603709570607482, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: ad40e378f39a19b149b009dee38b90e3211daf0cadc26f2bf0cba9c113417c3b

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.957, which indicates the subtask decomposition is already effective.
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
| `goal` | offset from task goal position (0.5009457299760202, 0.03603709570607482, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.5009457299760202, 0.03603709570607482, 0.025) | approach/contact targets near fixture |

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

## Current Skill (Q=0.268) — your mutation base

```yaml
skill: peg_insert
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
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
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: align_2
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

```

## Design Metrics

- **Composite score**: 0.268
- **task_score** (E): 0.841
- **fitness_score**: 0.528  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 0.00 | 0.1351 |
| align_lateral | 1.00 | 0.00 | 0.0305 |
| descend_to_entry | 1.00 | 1.00 | 0.0561 |
| insert_peg | 0.00 | 0.00 | 0.0324 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.482, -0.000, 0.169) | (0.504, -0.000, 0.340)→(0.486, -0.000, 0.209) | 0.260→0.132 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_lateral | align | 1.00 / step_budget | (0.482, -0.000, 0.169)→(0.488, -0.000, 0.139) | (0.486, -0.000, 0.209)→(0.493, -0.000, 0.179) | 0.132→0.104 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_to_entry | descend | 1.00 / step_budget | (0.488, -0.000, 0.139)→(0.480, -0.000, 0.084) | (0.493, -0.000, 0.179)→(0.485, -0.000, 0.124) | 0.104→0.054 | 1.00 / 1.000 | 240.291 | 240.291 |
| insert_peg | insert | 0.00 / guard_failure | (0.480, -0.000, 0.084)→(0.479, -0.000, 0.051) | (0.485, -0.000, 0.124)→(0.485, -0.000, 0.091) | 0.054→0.034 | 0.00 / 0.000 | 0.000 | 0.000 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.876
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.876
- phase_score: 0.392
- phase_breakdown.approach_socket_score: 0.198
- phase_breakdown.insertion_complete_score: 0.475

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.585
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.876
- **Median Q (composite search score)**: 0.249
- **K-run variance**: 0.0017
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.466


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `45273c8d1228632fd57317b0a02550505db6d7cbf023a115124b89e828802a94`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `70dcb1d9cf130ce66aaa294bb82afc0ceb52288177fb1bbf0b6209922022fad5`; realized-scene SHA-256: `ad40e378f39a19b149b009dee38b90e3211daf0cadc26f2bf0cba9c113417c3b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.50095,0.03604,0.025]},{"name":"target","value":[0.50095,0.03604,0.025]},{"name":"socket","value":[0.50095,0.03604,0.025]},{"name":"goal","value":[0.50095,0.03604,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.03604,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.50095,0.03604,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32075,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_lateral.lateral_offset_x":0.00959,"approach_above.approach_speed":0.07972,"descend_to_entry.descend_speed":0.03976,"insert_peg.insert_depth":0.05565},"optimized_scores":{"best_composite_score":0.24938,"best_fitness_score":0.50938,"best_task_score":0.8379},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.5118,0.03591,0.04985],"force_p95":231.62312,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":231.62312,"mean_force":231.62312,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.49696,0.03565,0.05188]}],"total_contact_groups":1},"final_pose_error":0.02739,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50095,0.03604,0.025],"final_tcp_position":[0.49699,0.03565,0.05144],"realised_fixture_position":[0.50095,0.03604,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50095,0.03604,0.08]},"peak_contact_force":231.62312,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":438.0,"n_steps_budget":1000.0,"object_pos_end":[0.50245,0.03239,0.20843],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.13248,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_socket","tcp_end":[0.49789,0.03236,0.16869],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":363.0,"n_steps_budget":600.0,"object_pos_end":[0.51106,0.03554,0.1771],"object_pos_start":[0.50245,0.03239,0.20843],"object_to_goal_dist_end":0.10398,"object_to_goal_dist_start":0.13248,"object_z_max":0.20843,"peak_contact_force":0.0,"phase_name":"align_lateral","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_socket","tcp_end":[0.50602,0.03548,0.13741],"tcp_start":[0.49789,0.03236,0.16869],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":287.0,"n_steps_budget":900.0,"object_pos_end":[0.50344,0.03575,0.12353],"object_pos_start":[0.51106,0.03554,0.1771],"object_to_goal_dist_end":0.05643,"object_to_goal_dist_start":0.10398,"object_z_max":0.1771,"peak_contact_force":231.62312,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":231.62312,"subtask_id":"approach_socket","tcp_end":[0.49794,0.03566,0.08391],"tcp_start":[0.50602,0.03548,0.13741],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":70.0,"n_steps_budget":600.0,"object_pos_end":[0.50281,0.03576,0.09102],"object_pos_start":[0.50344,0.03575,0.12353],"object_to_goal_dist_end":0.03752,"object_to_goal_dist_start":0.05643,"object_z_max":0.12353,"peak_contact_force":0.0,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion_complete","tcp_end":[0.49699,0.03565,0.05144],"tcp_start":[0.49794,0.03566,0.08391],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a0b26c055417598cbe086e53f7823e257fb75222f78e6d5a64925f365f02417e`; realized-scene SHA-256: `418fe4cae2076fb8f01886686f3853ea2b6261693c924940ce72258151551e93`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.48093,-0.01612,0.025]},{"name":"target","value":[0.48093,-0.01612,0.025]},{"name":"socket","value":[0.48093,-0.01612,0.025]},{"name":"goal","value":[0.48093,-0.01612,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,-0.01612,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.48093,-0.01612,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32941,"average_solve_count":85.0,"average_success_count":85.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_lateral.lateral_offset_x":0.00996,"approach_above.approach_speed":0.17295,"descend_to_entry.descend_speed":0.04813,"insert_peg.insert_depth":0.05112},"optimized_scores":{"best_composite_score":0.32547,"best_fitness_score":0.58547,"best_task_score":0.87611},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.49196,-0.01611,0.0498],"force_p95":237.38482,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":237.38482,"mean_force":237.38482,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.47712,-0.01604,0.05177]}],"total_contact_groups":1},"final_pose_error":0.02279,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.47715,-0.01604,0.05136],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":237.38482,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":375.0,"n_steps_budget":600.0,"object_pos_end":[0.48451,-0.01446,0.20926],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.13099,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_socket","tcp_end":[0.47994,-0.01445,0.16953],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":245.0,"n_steps_budget":600.0,"object_pos_end":[0.49094,-0.01583,0.17948],"object_pos_start":[0.48451,-0.01446,0.20926],"object_to_goal_dist_end":0.10114,"object_to_goal_dist_start":0.13099,"object_z_max":0.20926,"peak_contact_force":0.0,"phase_name":"align_lateral","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_socket","tcp_end":[0.48592,-0.01582,0.13979],"tcp_start":[0.47994,-0.01445,0.16953],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":309.0,"n_steps_budget":780.0,"object_pos_end":[0.48339,-0.01604,0.12348],"object_pos_start":[0.49094,-0.01583,0.17948],"object_to_goal_dist_end":0.04923,"object_to_goal_dist_start":0.10114,"object_z_max":0.17948,"peak_contact_force":237.38482,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":237.38482,"subtask_id":"approach_socket","tcp_end":[0.47793,-0.01602,0.08386],"tcp_start":[0.48592,-0.01582,0.13979],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":72.0,"n_steps_budget":600.0,"object_pos_end":[0.48293,-0.01607,0.09094],"object_pos_start":[0.48339,-0.01604,0.12348],"object_to_goal_dist_end":0.02587,"object_to_goal_dist_start":0.04923,"object_z_max":0.12348,"peak_contact_force":0.0,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion_complete","tcp_end":[0.47715,-0.01604,0.05136],"tcp_start":[0.47793,-0.01602,0.08386],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d263ae29be72790e561c8447b0a7b2ba7baa0aae40b60396cc4b2e04f6cc146d`; realized-scene SHA-256: `b2240da92884894b1100a1c972a50aa9dbe8b49daf4551e90009b821f1d87f37`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.46685,-0.02106,0.025]},{"name":"target","value":[0.46685,-0.02106,0.025]},{"name":"socket","value":[0.46685,-0.02106,0.025]},{"name":"goal","value":[0.46685,-0.02106,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,-0.02106,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.46685,-0.02106,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18447,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_lateral.lateral_offset_x":0.00892,"approach_above.approach_speed":0.10138,"descend_to_entry.descend_speed":0.03894,"insert_peg.insert_depth":0.04886},"optimized_scores":{"best_composite_score":0.22899,"best_fitness_score":0.48899,"best_task_score":0.8103},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.478,-0.02118,0.04994],"force_p95":251.86396,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":251.86396,"mean_force":251.86396,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.46315,-0.02093,0.05203]}],"total_contact_groups":1},"final_pose_error":0.0208,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.4632,-0.02093,0.05161],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":251.86396,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":412.0,"n_steps_budget":900.0,"object_pos_end":[0.4719,-0.01889,0.2094],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.13375,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_socket","tcp_end":[0.46736,-0.01888,0.16965],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":207.0,"n_steps_budget":600.0,"object_pos_end":[0.47594,-0.02059,0.18088],"object_pos_start":[0.4719,-0.01889,0.2094],"object_to_goal_dist_end":0.10573,"object_to_goal_dist_start":0.13375,"object_z_max":0.2094,"peak_contact_force":0.0,"phase_name":"align_lateral","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_socket","tcp_end":[0.47097,-0.02057,0.14119],"tcp_start":[0.46736,-0.01888,0.16965],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":330.0,"n_steps_budget":990.0,"object_pos_end":[0.4692,-0.02093,0.12355],"object_pos_start":[0.47594,-0.02059,0.18088],"object_to_goal_dist_end":0.0573,"object_to_goal_dist_start":0.10573,"object_z_max":0.18088,"peak_contact_force":251.86396,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":251.86396,"subtask_id":"approach_socket","tcp_end":[0.46379,-0.0209,0.08392],"tcp_start":[0.47097,-0.02057,0.14119],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":73.0,"n_steps_budget":600.0,"object_pos_end":[0.46891,-0.02097,0.0912],"object_pos_start":[0.4692,-0.02093,0.12355],"object_to_goal_dist_end":0.03914,"object_to_goal_dist_start":0.0573,"object_z_max":0.12355,"peak_contact_force":0.0,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion_complete","tcp_end":[0.4632,-0.02093,0.05161],"tcp_start":[0.46379,-0.0209,0.08392],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```