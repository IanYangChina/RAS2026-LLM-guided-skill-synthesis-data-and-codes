## Search State

- **Seed**: 1
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 3 | 0.2456 | 0.84 | ❌ rejected |
| 4 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.7475 | 0.96 | ❌ rejected |
| 3 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.7475 | 0.96 | ❌ rejected |
| 2 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.7475 | 0.96 | ❌ rejected |
| 1 | approach → align → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.2679 | 0.84 | ❌ rejected |

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

## Current Skill (Q=0.246) — your mutation base

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

- **Composite score**: 0.246
- **task_score** (E): 0.844
- **fitness_score**: 0.426  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.180

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.1578 |
| descend | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.465, 0.000, 0.147) | (0.504, -0.000, 0.340)→(0.502, 0.001, 0.133) | 0.260→0.054 | 1.00 / 1.667 | 204.957 | 312.230 |
| descend | contact | 0.00 / guard_failure | (0.465, 0.000, 0.147)→(0.465, 0.000, 0.147) | (0.502, 0.001, 0.133)→(0.502, 0.001, 0.133) | 0.054→0.054 | 1.00 / 2.000 | 320.238 | 1195.403 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.841
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.841
- phase_score: 0.190
- phase_breakdown.approach_socket_score: 0.633
- phase_breakdown.insert_peg_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.450
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.852
- **Median Q (composite search score)**: 0.240
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.333


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.06452,"average_solve_count":31.0,"average_success_count":31.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.1381,"descend.contact_force_threshold":6.26365,"insert.insertion_depth":0.05135},"optimized_scores":{"best_composite_score":0.2259,"best_fitness_score":0.4059,"best_task_score":0.85191},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":412.0,"contact_point_centroid":[0.56074,0.01537,0.07938],"force_p95":759.6677,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1204.44048,"mean_force":430.91947,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.45576,0.01564,0.17628]},{"body_a":"attachment","body_b":"peg_socket","contact_count":12.0,"contact_point_centroid":[0.46071,0.00446,0.07865],"force_p95":1033.16505,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1082.43279,"mean_force":314.35311,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.45593,0.00444,0.09151]},{"body_a":"peg_socket","body_b":"link7","contact_count":703.0,"contact_point_centroid":[0.55971,0.01758,0.07983],"force_p95":542.72948,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1081.61022,"mean_force":301.57665,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.45606,0.01294,0.16884]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.56082,0.02009,0.07999],"force_p95":272.17198,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":272.17198,"mean_force":272.17198,"phase_index":1.0,"phase_name":"descend","phase_type":"contact","tcp_position_centroid":[0.46391,0.01794,0.18473]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.55971,0.02072,0.08],"force_p95":238.03533,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":238.03533,"mean_force":238.03533,"phase_index":1.0,"phase_name":"descend","phase_type":"contact","tcp_position_centroid":[0.46391,0.01794,0.18473]},{"body_a":"attachment","body_b":"peg_socket","contact_count":5.0,"contact_point_centroid":[0.47101,0.00442,0.07982],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.45791,0.00442,0.09081]}],"total_contact_groups":6},"final_pose_error":0.08979,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50095,0.03604,0.025],"final_tcp_position":[0.46397,0.01783,0.18477],"realised_fixture_position":[0.50095,0.03604,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50095,0.03604,0.08]},"peak_contact_force":1204.44048,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":813.0,"n_steps_budget":900.0,"object_pos_end":[0.49873,0.019,0.16507],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08718,"object_to_goal_dist_start":0.26034,"object_z_max":0.3445,"peak_contact_force":272.17198,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2.0,"raw_peak_contact_force":272.17198,"subtask_id":"approach_socket","tcp_end":[0.46391,0.01794,0.18473],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49878,0.01892,0.1651],"object_pos_start":[0.49873,0.019,0.16507],"object_to_goal_dist_end":0.08719,"object_to_goal_dist_start":0.08718,"object_z_max":0.16507,"peak_contact_force":342.23351,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1132.0,"raw_peak_contact_force":1204.44048,"tcp_end":[0.46397,0.01783,0.18477],"tcp_start":[0.46391,0.01794,0.18473],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.08108,"average_solve_count":37.0,"average_success_count":37.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.08285,"descend.contact_force_threshold":11.82618,"insert.insertion_depth":0.04706},"optimized_scores":{"best_composite_score":0.27041,"best_fitness_score":0.45041,"best_task_score":0.84097},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":908.0,"contact_point_centroid":[0.54069,-0.00667,0.0798],"force_p95":318.63653,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1440.50497,"mean_force":308.4012,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.46666,-0.00312,0.13352]},{"body_a":"attachment","body_b":"peg_socket","contact_count":16.0,"contact_point_centroid":[0.44368,-0.00472,0.07765],"force_p95":819.46879,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":889.24707,"mean_force":196.35813,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.44016,-0.0016,0.08822]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54069,-0.0089,0.07991],"force_p95":341.85993,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":341.85993,"mean_force":341.85993,"phase_index":1.0,"phase_name":"descend","phase_type":"contact","tcp_position_centroid":[0.46933,-0.00631,0.13796]}],"total_contact_groups":3},"final_pose_error":0.03634,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.46936,-0.00625,0.138],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":1440.50497,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50776,-0.00609,0.12687],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.0479,"object_to_goal_dist_start":0.26034,"object_z_max":0.34439,"peak_contact_force":341.85993,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1.0,"raw_peak_contact_force":341.85993,"subtask_id":"approach_socket","tcp_end":[0.46933,-0.00631,0.13796],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50778,-0.00606,0.12689],"object_pos_start":[0.50776,-0.00609,0.12687],"object_to_goal_dist_end":0.04792,"object_to_goal_dist_start":0.0479,"object_z_max":0.12687,"peak_contact_force":333.14133,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":924.0,"raw_peak_contact_force":1440.50497,"tcp_end":[0.46936,-0.00625,0.138],"tcp_start":[0.46933,-0.00631,0.13796],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.05405,"average_solve_count":37.0,"average_success_count":37.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.08003,"descend.contact_force_threshold":11.65618,"insert.insertion_depth":0.04227},"optimized_scores":{"best_composite_score":0.24044,"best_fitness_score":0.42044,"best_task_score":0.83849},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":905.0,"contact_point_centroid":[0.52666,-0.01092,0.06642],"force_p95":339.33748,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":941.26207,"mean_force":310.34528,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.45788,-0.00787,0.11624]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.4491,0.00927,0.07976],"force_p95":689.71071,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":693.2582,"mean_force":614.07326,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.44633,-0.00236,0.08802]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.67945,-0.00972,-0.0],"force_p95":322.65829,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":322.65829,"mean_force":322.65829,"phase_index":1.0,"phase_name":"descend","phase_type":"contact","tcp_position_centroid":[0.4617,-0.01013,0.1195]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.52677,-0.01383,0.06353],"force_p95":167.99738,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":167.99738,"mean_force":167.99738,"phase_index":1.0,"phase_name":"descend","phase_type":"contact","tcp_position_centroid":[0.4617,-0.01013,0.1195]},{"body_a":"world","body_b":"link6","contact_count":290.0,"contact_point_centroid":[0.67911,-0.00848,-1e-05],"force_p95":47.6722,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":154.3568,"mean_force":24.79823,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.46195,-0.00856,0.12055]},{"body_a":"attachment","body_b":"peg_socket","contact_count":63.0,"contact_point_centroid":[0.52685,-0.00992,0.07999],"force_p95":99.89448,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":150.55655,"mean_force":88.08084,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.46169,-0.00996,0.11951]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.52685,-0.01015,0.07999],"force_p95":147.16486,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":147.16486,"mean_force":147.16486,"phase_index":1.0,"phase_name":"descend","phase_type":"contact","tcp_position_centroid":[0.4617,-0.01013,0.1195]},{"body_a":"attachment","body_b":"peg_socket","contact_count":8.0,"contact_point_centroid":[0.43648,0.00373,0.07992],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.4351,-0.00951,0.08674]}],"total_contact_groups":8},"final_pose_error":0.0189,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.46171,-0.01008,0.1195],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":941.26207,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49931,-0.01017,0.10589],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.02782,"object_to_goal_dist_start":0.26034,"object_z_max":0.34437,"peak_contact_force":0.84023,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3.0,"raw_peak_contact_force":322.65829,"subtask_id":"approach_socket","tcp_end":[0.4617,-0.01013,0.1195],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49932,-0.01013,0.1059],"object_pos_start":[0.49931,-0.01017,0.10589],"object_to_goal_dist_end":0.02782,"object_to_goal_dist_start":0.02782,"object_z_max":0.10589,"peak_contact_force":285.34043,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1270.0,"raw_peak_contact_force":941.26207,"tcp_end":[0.46171,-0.01008,0.1195],"tcp_start":[0.4617,-0.01013,0.1195],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```