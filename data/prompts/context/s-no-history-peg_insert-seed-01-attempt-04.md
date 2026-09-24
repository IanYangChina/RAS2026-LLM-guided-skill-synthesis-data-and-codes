## Search State

- **Seed**: 1
- **Iteration**: 5 / 15

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

## Current Skill (Q=0.549) — your mutation base

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

- **Composite score**: 0.549
- **task_score** (E): 0.853
- **fitness_score**: 0.759  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| rotate_1 | 1.00 | 0.00 | 0.2132 |
| align_1 | 1.00 | 0.00 | 0.0092 |
| push_1 | 1.00 | 1.00 | 0.0314 |
| align_2 | 1.00 | 1.00 | 0.0035 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| rotate_1 | approach | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.480, -0.001, 0.090) | (0.504, -0.000, 0.340)→(0.481, -0.001, 0.130) | 0.260→0.060 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_1 | align | 1.00 / step_budget | (0.480, -0.001, 0.090)→(0.483, -0.001, 0.081) | (0.481, -0.001, 0.130)→(0.484, -0.001, 0.121) | 0.060→0.052 | 0.00 / 0.000 | 0.000 | 0.000 |
| push_1 | push | 1.00 / time_limit | (0.483, -0.001, 0.081)→(0.489, -0.001, 0.050) | (0.484, -0.001, 0.121)→(0.490, -0.001, 0.090) | 0.052→0.032 | 1.00 / 1.000 | 444.799 | 499.503 |
| align_2 | align | 1.00 / step_budget | (0.489, -0.001, 0.050)→(0.492, -0.001, 0.051) | (0.490, -0.001, 0.090)→(0.490, -0.001, 0.091) | 0.032→0.032 | 1.00 / 1.000 | 301.152 | 323.809 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.891
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.891
- phase_score: 0.700
- phase_breakdown.insert_peg_score: 0.578
- phase_breakdown.approach_socket_score: 0.983

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.776
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.891
- **Median Q (composite search score)**: 0.541
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.356


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47619,"average_solve_count":105.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00636,"align_2.lateral_offset_x":-0.00986,"push_1.push_distance":0.04167},"optimized_scores":{"best_composite_score":0.53848,"best_fitness_score":0.74848,"best_task_score":0.8445},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":374.0,"contact_point_centroid":[0.51642,0.03758,0.04994],"force_p95":465.03615,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":483.24274,"mean_force":429.91264,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50171,0.03477,0.05021]},{"body_a":"attachment","body_b":"peg_socket","contact_count":480.0,"contact_point_centroid":[0.49787,0.03596,0.04995],"force_p95":300.32801,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":305.3171,"mean_force":260.3152,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50848,0.0355,0.05035]}],"total_contact_groups":2},"final_pose_error":0.03175,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50095,0.03604,0.025],"final_tcp_position":[0.50972,0.03573,0.0507],"realised_fixture_position":[0.50095,0.03604,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50095,0.03604,0.08]},"peak_contact_force":483.24274,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49772,0.03215,0.1378],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.06618,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_socket","tcp_end":[0.49727,0.03213,0.09781],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":82.0,"n_steps_budget":600.0,"object_pos_end":[0.5012,0.03431,0.12334],"object_pos_start":[0.49772,0.03215,0.1378],"object_to_goal_dist_end":0.05529,"object_to_goal_dist_start":0.06618,"object_z_max":0.1378,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_socket","tcp_end":[0.50038,0.03426,0.08335],"tcp_start":[0.49727,0.03213,0.09781],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":539.0,"n_steps_budget":630.0,"object_pos_end":[0.50839,0.03534,0.09067],"object_pos_start":[0.5012,0.03431,0.12334],"object_to_goal_dist_end":0.03785,"object_to_goal_dist_start":0.05529,"object_z_max":0.12334,"peak_contact_force":413.26296,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":374.0,"raw_peak_contact_force":483.24274,"subtask_id":"insert_peg","tcp_end":[0.50633,0.03495,0.05072],"tcp_start":[0.50038,0.03426,0.08335],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.50757,0.03563,0.09065],"object_pos_start":[0.50839,0.03534,0.09067],"object_to_goal_dist_end":0.03795,"object_to_goal_dist_start":0.03785,"object_z_max":0.09073,"peak_contact_force":285.76087,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":480.0,"raw_peak_contact_force":305.3171,"subtask_id":"insert_peg","tcp_end":[0.50972,0.03573,0.0507],"tcp_start":[0.50633,0.03495,0.05072],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.39623,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00866,"align_2.lateral_offset_x":-0.00945,"push_1.push_distance":0.03191},"optimized_scores":{"best_composite_score":0.56607,"best_fitness_score":0.77607,"best_task_score":0.89086},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":338.0,"contact_point_centroid":[0.49732,-0.018,0.04993],"force_p95":489.98934,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":503.37758,"mean_force":458.9305,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48251,-0.01585,0.05003]},{"body_a":"attachment","body_b":"peg_socket","contact_count":481.0,"contact_point_centroid":[0.47733,-0.0165,0.04994],"force_p95":317.77304,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":323.30853,"mean_force":281.05298,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.48911,-0.01618,0.05033]}],"total_contact_groups":2},"final_pose_error":0.03193,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.49039,-0.01628,0.05073],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":503.37758,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47886,-0.01527,0.12673],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.05352,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_socket","tcp_end":[0.47843,-0.01526,0.08674],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":59.0,"n_steps_budget":600.0,"object_pos_end":[0.48238,-0.01569,0.12014],"object_pos_start":[0.47886,-0.01527,0.12673],"object_to_goal_dist_end":0.04656,"object_to_goal_dist_start":0.05352,"object_z_max":0.12673,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_socket","tcp_end":[0.48164,-0.01567,0.08015],"tcp_start":[0.47843,-0.01526,0.08674],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":493.0,"n_steps_budget":600.0,"object_pos_end":[0.48816,-0.01606,0.09034],"object_pos_start":[0.48238,-0.01569,0.12014],"object_to_goal_dist_end":0.02247,"object_to_goal_dist_start":0.04656,"object_z_max":0.12014,"peak_contact_force":446.32072,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":338.0,"raw_peak_contact_force":503.37758,"subtask_id":"insert_peg","tcp_end":[0.48704,-0.01594,0.05035],"tcp_start":[0.48164,-0.01567,0.08015],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.48817,-0.01622,0.09066],"object_pos_start":[0.48816,-0.01606,0.09034],"object_to_goal_dist_end":0.02273,"object_to_goal_dist_start":0.02247,"object_z_max":0.09066,"peak_contact_force":299.6749,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":481.0,"raw_peak_contact_force":323.30853,"subtask_id":"insert_peg","tcp_end":[0.49039,-0.01628,0.05073],"tcp_start":[0.48704,-0.01594,0.05035],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36792,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00821,"align_2.lateral_offset_x":-0.00999,"push_1.push_distance":0.02035},"optimized_scores":{"best_composite_score":0.54103,"best_fitness_score":0.75103,"best_task_score":0.82459},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":298.0,"contact_point_centroid":[0.47834,-0.02911,0.04992],"force_p95":490.84348,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":511.88776,"mean_force":469.72404,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46804,-0.02072,0.0499]},{"body_a":"attachment","body_b":"peg_socket","contact_count":484.0,"contact_point_centroid":[0.46079,-0.02157,0.04994],"force_p95":337.02863,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":342.80031,"mean_force":304.94632,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.47411,-0.02096,0.05033]}],"total_contact_groups":2},"final_pose_error":0.03179,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.47554,-0.02111,0.05073],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":511.88776,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46529,-0.02009,0.12526],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.06047,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_socket","tcp_end":[0.46488,-0.02008,0.08526],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":46.0,"n_steps_budget":600.0,"object_pos_end":[0.4678,-0.02048,0.12043],"object_pos_start":[0.46529,-0.02009,0.12526],"object_to_goal_dist_end":0.05559,"object_to_goal_dist_start":0.06047,"object_z_max":0.12526,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_socket","tcp_end":[0.46712,-0.02046,0.08043],"tcp_start":[0.46488,-0.02008,0.08526],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":463.0,"n_steps_budget":600.0,"object_pos_end":[0.47248,-0.02096,0.09006],"object_pos_start":[0.4678,-0.02048,0.12043],"object_to_goal_dist_end":0.03602,"object_to_goal_dist_start":0.05559,"object_z_max":0.12043,"peak_contact_force":474.81481,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":298.0,"raw_peak_contact_force":511.88776,"subtask_id":"insert_peg","tcp_end":[0.47214,-0.02086,0.05006],"tcp_start":[0.46712,-0.02046,0.08043],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.47331,-0.02104,0.09066],"object_pos_start":[0.47248,-0.02096,0.09006],"object_to_goal_dist_end":0.03562,"object_to_goal_dist_start":0.03602,"object_z_max":0.09066,"peak_contact_force":318.02128,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":484.0,"raw_peak_contact_force":342.80031,"subtask_id":"insert_peg","tcp_end":[0.47554,-0.02111,0.05073],"tcp_start":[0.47214,-0.02086,0.05006],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```