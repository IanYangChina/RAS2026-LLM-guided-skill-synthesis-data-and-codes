## Search State

- **Seed**: 7
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | -0.3864 | 0.15 | ❌ rejected |
| 0 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ✅ accepted |

**Proposal policy**: task_score is 0.15 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: grasp_place
- Frozen realised-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`
- Frozen object start: [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5, 0.0, 0.3)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5125095466604667, 0.039721380096957554, 0.03)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5125095466604667, 0.039721380096957554, 0.03]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5125, 0.0397, 0.03]
  frozen_task_target: [0.6276, 0.1725, 0.145]
  frozen_object_starts: {'grasp_target': [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]}
  frozen_targets: {'place_target': [0.5, 0.0, 0.3]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6

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
| `object` | offset from object initial position (0.6275685690245193, 0.17252071899905919, 0.14502494273668382) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

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

## Current Skill (Q=-0.386) — your mutation base

```yaml
skill: grasp_place
skill_type: arm_gripper
phases:
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: insert_1
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: pose_tolerance
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
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
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
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2

```

## Design Metrics

- **Composite score**: -0.386
- **task_score** (E): 0.145
- **fitness_score**: 0.144  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.530

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_object | 0.00 | 1.00 | 0.1708 |
| descend_to_grasp | 0.00 | 1.00 | 0.0423 |
| grasp | 1.00 | 1.00 | 0.0000 |
| lift | 0.00 | 1.00 | 0.1502 |
| transport_to_goal | 0.00 | 1.00 | 0.1541 |
| descend_to_place | 0.00 | 1.00 | 0.0698 |
| release | 1.00 | 1.00 | 0.0185 |
| retract_from_goal | 0.00 | 1.00 | 0.0097 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.406, 0.005, 0.158) | (0.511, 0.022, 0.030)→(0.471, 0.025, 0.016) | 0.271→0.295 | 1.00 / 5.000 | 194.311 | 1358.786 |
| descend_to_grasp | descend | 0.00 / step_budget | (0.406, 0.005, 0.158)→(0.418, 0.008, 0.197) | (0.471, 0.025, 0.016)→(0.471, 0.025, 0.016) | 0.295→0.295 | 1.00 / 5.000 | 256.877 | 453.194 |
| grasp | grasp | 1.00 / step_budget | (0.419, 0.008, 0.196)→(0.419, 0.008, 0.196) | (0.471, 0.025, 0.016)→(0.471, 0.025, 0.016) | 0.295→0.295 | 1.00 / 9.667 | 182031.453 | 151.741 |
| lift | lift | 0.00 / step_budget | (0.417, 0.008, 0.284)→(0.411, 0.008, 0.434) | (0.471, 0.025, 0.016)→(0.471, 0.025, 0.016) | 0.295→0.295 | 1.00 / 8.000 | 3249.675 | 87.980 |
| transport_to_goal | approach | 0.00 / step_budget | (0.411, 0.008, 0.434)→(0.479, 0.085, 0.321) | (0.471, 0.025, 0.016)→(0.471, 0.025, 0.016) | 0.295→0.295 | 1.00 / 8.000 | 91019.042 | 0.123 |
| descend_to_place | descend | 0.00 / step_budget | (0.479, 0.085, 0.321)→(0.515, 0.125, 0.276) | (0.471, 0.025, 0.016)→(0.471, 0.025, 0.016) | 0.295→0.295 | 1.00 / 9.667 | 91123.154 | 288.246 |
| release | release | 1.00 / step_budget | (0.515, 0.125, 0.276)→(0.515, 0.126, 0.295) | (0.471, 0.025, 0.016)→(0.471, 0.025, 0.016) | 0.295→0.295 | 1.00 / 5.333 | 151.012 | 193.383 |
| retract_from_goal | retract | 0.00 / step_budget | (0.515, 0.126, 0.295)→(0.516, 0.133, 0.291) | (0.471, 0.025, 0.016)→(0.471, 0.025, 0.016) | 0.295→0.295 | 1.00 / 5.333 | 150.919 | 147.825 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.205
- phase_score: 0.040
- phase_breakdown.reach_pre_grasp_score: 0.092
- phase_breakdown.reach_goal_score: 0.018
- grasp_place_fitness: 0.175

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.175
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.205
- **Median Q (composite search score)**: -0.390
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.391


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `0b279c554151a1bc107b4895d67067efa2444eadb5a644f2482f57ab9ff93d7f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `079d4532bc3cff86c1b89933c7940f2ee474dc4233e12f8d134c76ceb3cd8d4d`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.62757,0.17252,0.14502]},{"name":"goal","value":[0.51251,0.03972,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":122.0,"average_failure_rate":0.41077,"average_mean_iterations":85.38384,"average_solve_count":297.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_speed":0.03915,"descend_to_grasp.descend_speed":0.02415,"descend_to_place.place_speed":0.03022,"lift.lift_height":0.20951,"lift.lift_speed":0.05656,"retract_from_goal.retract_speed":0.06181,"transport_to_goal.transport_speed":0.09315},"optimized_scores":{"best_composite_score":-0.35526,"best_fitness_score":0.17474,"best_task_score":0.20502},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.63369,0.00605,-0.00046],"force_p95":197.91973,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1336.19108,"mean_force":200.83709,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.39256,0.00567,0.12335]},{"body_a":"link5","body_b":"hand","contact_count":185.0,"contact_point_centroid":[0.54561,0.03654,0.24834],"force_p95":388.33693,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":455.56244,"mean_force":338.81779,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.51804,0.11338,0.27451]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.54254,0.05534,0.22624],"force_p95":314.45174,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":316.13909,"mean_force":265.68336,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.52688,0.12449,0.27712]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.6146,0.01401,-0.00025],"force_p95":199.32061,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":241.67313,"mean_force":196.88545,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.39146,0.01423,0.15564]},{"body_a":"link5","body_b":"hand","contact_count":1.0,"contact_point_centroid":[0.5456,0.05657,0.24624],"force_p95":176.78604,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":176.78604,"mean_force":176.78604,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.52757,0.12479,0.29752]},{"body_a":"world","body_b":"link6","contact_count":6.0,"contact_point_centroid":[0.60295,0.01891,-0.0001],"force_p95":84.3341,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":84.93879,"mean_force":69.42755,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.40475,0.01839,0.18769]},{"body_a":"world","body_b":"link6","contact_count":500.0,"contact_point_centroid":[0.6028,0.01895,-0.00014],"force_p95":82.13079,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":83.94823,"mean_force":75.16519,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4047,0.01841,0.18774]},{"body_a":"grasp_target","body_b":"link7","contact_count":347.0,"contact_point_centroid":[0.49297,0.02328,0.04139],"force_p95":1.28391,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.25555,"mean_force":0.48061,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.3876,0.00381,0.10221]},{"body_a":"grasp_target","body_b":"hand","contact_count":316.0,"contact_point_centroid":[0.48587,0.02423,0.05475],"force_p95":1.81427,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.70028,"mean_force":0.43059,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.38733,0.00373,0.10042]},{"body_a":"world","body_b":"grasp_target","contact_count":3231.0,"contact_point_centroid":[0.48219,0.04762,-0.00285],"force_p95":0.36421,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.36249,"mean_force":0.19297,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.4079,0.00562,0.13769]},{"body_a":"left_finger","body_b":"link5","contact_count":89.0,"contact_point_centroid":[0.51084,0.09229,0.27285],"force_p95":0.7217,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.78818,"mean_force":0.50079,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.52746,0.1247,0.28888]},{"body_a":"left_finger","body_b":"link5","contact_count":2.0,"contact_point_centroid":[0.5114,0.0926,0.28115],"force_p95":0.6102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.63866,"mean_force":0.35412,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.52757,0.12479,0.29752]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.4697,0.05032,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.39146,0.01423,0.15564]},{"body_a":"world","body_b":"grasp_target","contact_count":2000.0,"contact_point_centroid":[0.4697,0.05032,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4047,0.01841,0.18774]},{"body_a":"world","body_b":"grasp_target","contact_count":7648.0,"contact_point_centroid":[0.4697,0.05032,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4029,0.01838,0.31104]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.4697,0.05032,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.449,0.05418,0.39008]}],"total_contact_groups":25},"final_pose_error":0.11083,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.4697,0.05032,0.01602],"final_tcp_position":[0.52757,0.1248,0.29773],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":9748.97142,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4697,0.05032,0.01602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.2377,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":193.02339,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4800.0,"raw_peak_contact_force":1336.19108,"subtask_id":"reach_pre_grasp","tcp_end":[0.40076,0.00921,0.15082],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15688,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4697,0.05032,0.01602],"object_pos_start":[0.4697,0.05032,0.01602],"object_to_goal_dist_end":0.2377,"object_to_goal_dist_start":0.2377,"object_z_max":0.01602,"peak_contact_force":198.33382,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5000.0,"raw_peak_contact_force":241.67313,"tcp_end":[0.40439,0.01841,0.18785],"tcp_start":[0.40076,0.00921,0.15082],"tcp_to_object_dist_end":0.18657,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":100.0,"n_steps_budget":50.0,"object_pos_end":[0.4697,0.05032,0.01602],"object_pos_start":[0.4697,0.05032,0.01602],"object_to_goal_dist_end":0.2377,"object_to_goal_dist_start":0.2377,"object_z_max":0.01602,"peak_contact_force":86.11627,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3040.0,"raw_peak_contact_force":83.94823,"tcp_end":[0.40476,0.01839,0.18764],"tcp_start":[0.40476,0.01839,0.18765],"tcp_to_object_dist_end":0.18625,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1912.0,"n_steps_budget":1000.0,"object_pos_end":[0.4697,0.05032,0.01602],"object_pos_start":[0.4697,0.05032,0.01602],"object_to_goal_dist_end":0.2377,"object_to_goal_dist_start":0.2377,"object_z_max":0.01602,"peak_contact_force":9748.78009,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15767.0,"raw_peak_contact_force":84.93879,"tcp_end":[0.39921,0.01949,0.46186],"tcp_start":[0.40366,0.0183,0.29552],"tcp_to_object_dist_end":0.45243,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4697,0.05032,0.01602],"object_pos_start":[0.4697,0.05032,0.01602],"object_to_goal_dist_end":0.2377,"object_to_goal_dist_start":0.2377,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8262.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.47785,0.07554,0.33788],"tcp_start":[0.39921,0.01949,0.46186],"tcp_to_object_dist_end":0.32295,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":361.0,"n_steps_budget":1000.0,"object_pos_end":[0.4697,0.05032,0.01602],"object_pos_start":[0.4697,0.05032,0.01602],"object_to_goal_dist_end":0.2377,"object_to_goal_dist_start":0.2377,"object_z_max":0.01602,"peak_contact_force":338.32928,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3176.0,"raw_peak_contact_force":455.56244,"tcp_end":[0.52635,0.12454,0.27475],"tcp_start":[0.47785,0.07554,0.33788],"tcp_to_object_dist_end":0.27506,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4697,0.05032,0.01602],"object_pos_start":[0.4697,0.05032,0.01602],"object_to_goal_dist_end":0.2377,"object_to_goal_dist_start":0.2377,"object_z_max":0.01602,"peak_contact_force":255.09101,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1315.0,"raw_peak_contact_force":316.13909,"tcp_end":[0.52757,0.12479,0.29752],"tcp_start":[0.52635,0.12454,0.27475],"tcp_to_object_dist_end":0.29688,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.4697,0.05032,0.01602],"object_pos_start":[0.4697,0.05032,0.01602],"object_to_goal_dist_end":0.2377,"object_to_goal_dist_start":0.2377,"object_z_max":0.01602,"peak_contact_force":185.41462,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":7.0,"raw_peak_contact_force":176.78604,"tcp_end":[0.52757,0.1248,0.29773],"tcp_start":[0.52757,0.12479,0.29752],"tcp_to_object_dist_end":0.29708,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a74f7c08b88460953bfa7e35b953cddf9278fdc17d2d4db8a2ea121b328e8b73`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.58187,0.22885,0.23048]},{"name":"goal","value":[0.4827,0.04873,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":49.0,"average_failure_rate":0.17818,"average_mean_iterations":39.4,"average_solve_count":275.0,"average_success_count":226.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_speed":0.04763,"descend_to_grasp.descend_speed":0.01208,"descend_to_place.place_speed":0.02306,"lift.lift_height":0.16403,"lift.lift_speed":0.02718,"retract_from_goal.retract_speed":0.04779,"transport_to_goal.transport_speed":0.1239},"optimized_scores":{"best_composite_score":-0.39023,"best_fitness_score":0.13977,"best_task_score":0.12459},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.63051,0.00792,-0.00047],"force_p95":199.22423,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1332.92147,"mean_force":202.93078,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.38746,0.00741,0.12008]},{"body_a":"link5","body_b":"hand","contact_count":80.0,"contact_point_centroid":[0.54477,0.06977,0.2681],"force_p95":378.88125,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":409.05184,"mean_force":310.18124,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.50767,0.15587,0.28141]},{"body_a":"world","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.52698,0.00926,-0.0029],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":399.0517,"mean_force":19.00246,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.37152,0.00383,0.05158]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.61317,0.01807,-0.00025],"force_p95":199.90212,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":269.39172,"mean_force":198.14405,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.38925,0.01818,0.15464]},{"body_a":"link5","body_b":"hand","contact_count":35.0,"contact_point_centroid":[0.54359,0.07807,0.26842],"force_p95":265.42538,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":266.56768,"mean_force":250.43419,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.51075,0.16474,0.2932]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.54123,0.07021,0.25396],"force_p95":256.92499,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":263.88828,"mean_force":199.75417,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.51072,0.15787,0.28157]},{"body_a":"world","body_b":"link6","contact_count":8.0,"contact_point_centroid":[0.60213,0.02336,-0.00011],"force_p95":78.58415,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":85.45537,"mean_force":62.26201,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.40115,0.02254,0.1847]},{"body_a":"world","body_b":"link6","contact_count":500.0,"contact_point_centroid":[0.60197,0.02339,-0.00014],"force_p95":82.71794,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":84.92924,"mean_force":75.17543,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4011,0.02256,0.18476]},{"body_a":"grasp_target","body_b":"hand","contact_count":43.0,"contact_point_centroid":[0.46052,0.03787,0.03983],"force_p95":3.84196,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.91732,"mean_force":1.76713,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.381,0.0039,0.0556]},{"body_a":"grasp_target","body_b":"link7","contact_count":28.0,"contact_point_centroid":[0.48467,0.02965,0.01346],"force_p95":0.77838,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.12742,"mean_force":0.52907,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.3722,0.00386,0.05541]},{"body_a":"world","body_b":"grasp_target","contact_count":3912.0,"contact_point_centroid":[0.44767,0.04934,-0.00214],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.43174,"mean_force":0.14069,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.39988,0.00698,0.13016]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.44261,0.04939,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.38925,0.01818,0.15464]},{"body_a":"world","body_b":"grasp_target","contact_count":2000.0,"contact_point_centroid":[0.44261,0.04939,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4011,0.02256,0.18476]},{"body_a":"world","body_b":"grasp_target","contact_count":7592.0,"contact_point_centroid":[0.44261,0.04939,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.39953,0.02242,0.29311]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.44261,0.04939,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.43833,0.07133,0.38025]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.44261,0.04939,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.48867,0.13534,0.29606]}],"total_contact_groups":23},"final_pose_error":0.13137,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.44261,0.04939,0.01602],"final_tcp_position":[0.51138,0.17205,0.28529],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273031.01064,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44261,0.04939,0.01602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.31241,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":197.42827,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4890.0,"raw_peak_contact_force":1332.92147,"subtask_id":"reach_pre_grasp","tcp_end":[0.39314,0.01232,0.14332],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14151,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44261,0.04939,0.01602],"object_pos_start":[0.44261,0.04939,0.01602],"object_to_goal_dist_end":0.31241,"object_to_goal_dist_start":0.31241,"object_z_max":0.01602,"peak_contact_force":198.50483,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5000.0,"raw_peak_contact_force":269.39172,"tcp_end":[0.40077,0.02256,0.18488],"tcp_start":[0.39314,0.01232,0.14332],"tcp_to_object_dist_end":0.17602,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":100.0,"n_steps_budget":50.0,"object_pos_end":[0.44261,0.04939,0.01602],"object_pos_start":[0.44261,0.04939,0.01602],"object_to_goal_dist_end":0.31241,"object_to_goal_dist_start":0.31241,"object_z_max":0.01602,"peak_contact_force":273004.12064,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3038.0,"raw_peak_contact_force":84.92924,"tcp_end":[0.40116,0.02254,0.18466],"tcp_start":[0.40116,0.02255,0.18467],"tcp_to_object_dist_end":0.17572,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1898.0,"n_steps_budget":1000.0,"object_pos_end":[0.44261,0.04939,0.01602],"object_pos_start":[0.44261,0.04939,0.01602],"object_to_goal_dist_end":0.31241,"object_to_goal_dist_start":0.31241,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15627.0,"raw_peak_contact_force":85.45537,"tcp_end":[0.39949,0.02268,0.4327],"tcp_start":[0.3999,0.02244,0.28299],"tcp_to_object_dist_end":0.41975,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44261,0.04939,0.01602],"object_pos_start":[0.44261,0.04939,0.01602],"object_to_goal_dist_end":0.31241,"object_to_goal_dist_start":0.31241,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8266.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.46869,0.11072,0.32815],"tcp_start":[0.39949,0.02268,0.4327],"tcp_to_object_dist_end":0.31916,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44261,0.04939,0.01602],"object_pos_start":[0.44261,0.04939,0.01602],"object_to_goal_dist_end":0.31241,"object_to_goal_dist_start":0.31241,"object_z_max":0.01602,"peak_contact_force":273031.01064,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8418.0,"raw_peak_contact_force":409.05184,"tcp_end":[0.51033,0.15717,0.27886],"tcp_start":[0.46869,0.11072,0.32815],"tcp_to_object_dist_end":0.29204,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.44261,0.04939,0.01602],"object_pos_start":[0.44261,0.04939,0.01602],"object_to_goal_dist_end":0.31241,"object_to_goal_dist_start":0.31241,"object_z_max":0.01602,"peak_contact_force":197.82163,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1224.0,"raw_peak_contact_force":263.88828,"tcp_end":[0.51114,0.15847,0.30173],"tcp_start":[0.51033,0.15717,0.27886],"tcp_to_object_dist_end":0.31341,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":35.0,"n_steps_budget":1000.0,"object_pos_end":[0.44261,0.04939,0.01602],"object_pos_start":[0.44261,0.04939,0.01602],"object_to_goal_dist_end":0.31241,"object_to_goal_dist_start":0.31241,"object_z_max":0.01602,"peak_contact_force":267.22056,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":175.0,"raw_peak_contact_force":266.56768,"tcp_end":[0.51138,0.17205,0.28529],"tcp_start":[0.51114,0.15847,0.30173],"tcp_to_object_dist_end":0.30379,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b1a72366a9c9a56aa2e80fc4399e157c8281abf492ab3c1ede02058762a86ed7`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.61031,0.22775,0.20741]},{"name":"goal","value":[0.53702,-0.02132,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":145.0,"average_failure_rate":0.48333,"average_mean_iterations":100.03,"average_solve_count":300.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_speed":0.0641,"descend_to_grasp.descend_speed":0.07983,"descend_to_place.place_speed":0.03214,"lift.lift_height":0.20047,"lift.lift_speed":0.03452,"retract_from_goal.retract_speed":0.06884,"transport_to_goal.transport_speed":0.10718},"optimized_scores":{"best_composite_score":-0.41376,"best_fitness_score":0.11624,"best_task_score":0.10651},"replay_outcomes":[{"contacts":{"omitted_contact_groups":6,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.63662,-0.00418,-0.00046],"force_p95":200.92412,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1407.24694,"mean_force":199.89357,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.4048,-0.00421,0.13821]},{"body_a":"world","body_b":"link6","contact_count":999.0,"contact_point_centroid":[0.61171,-0.00748,-0.00025],"force_p95":411.61788,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":848.51782,"mean_force":250.00205,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.41914,-0.01119,0.1957]},{"body_a":"world","body_b":"link6","contact_count":500.0,"contact_point_centroid":[0.62794,-0.01027,-0.00014],"force_p95":105.06249,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":286.34584,"mean_force":78.90215,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45002,-0.01633,0.21615]},{"body_a":"world","body_b":"link6","contact_count":7.0,"contact_point_centroid":[0.62809,-0.0103,-0.0001],"force_p95":92.77832,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":93.54647,"mean_force":82.91849,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45002,-0.01635,0.21611]},{"body_a":"grasp_target","body_b":"link7","contact_count":356.0,"contact_point_centroid":[0.52175,-0.01439,0.03316],"force_p95":1.08393,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.54068,"mean_force":0.40488,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.39404,-0.00264,0.10748]},{"body_a":"grasp_target","body_b":"link6","contact_count":109.0,"contact_point_centroid":[0.5405,-0.02655,0.02885],"force_p95":0.8944,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.53876,"mean_force":0.47268,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.38569,-0.00229,0.0865]},{"body_a":"grasp_target","body_b":"hand","contact_count":113.0,"contact_point_centroid":[0.4935,-0.02718,0.04677],"force_p95":2.31878,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.08873,"mean_force":0.92631,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.38775,-0.00226,0.08089]},{"body_a":"world","body_b":"grasp_target","contact_count":3720.0,"contact_point_centroid":[0.50716,-0.02515,-0.00225],"force_p95":0.2717,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.83528,"mean_force":0.15468,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.41721,-0.00399,0.14911]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50154,-0.02597,-0.00199],"force_p95":0.123,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13202,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.41913,-0.01119,0.19568]},{"body_a":"world","body_b":"grasp_target","contact_count":2000.0,"contact_point_centroid":[0.50153,-0.02598,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45002,-0.01633,0.21615]},{"body_a":"world","body_b":"grasp_target","contact_count":7648.0,"contact_point_centroid":[0.50153,-0.02598,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44377,-0.01689,0.29311]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50153,-0.02598,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.46509,0.02479,0.35719]},{"body_a":"world","body_b":"grasp_target","contact_count":740.0,"contact_point_centroid":[0.50153,-0.02598,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.4991,0.08283,0.28088]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50153,-0.02598,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.50534,0.09584,0.26575]},{"body_a":"world","body_b":"grasp_target","contact_count":64.0,"contact_point_centroid":[0.50153,-0.02598,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.5062,0.09745,0.28667]},{"body_a":"grasp_target","body_b":"link6","contact_count":73.0,"contact_point_centroid":[0.53008,-0.01115,0.03606],"force_p95":0.02039,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.02242,"mean_force":0.01548,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.39064,-0.00873,0.15672]}],"total_contact_groups":22},"final_pose_error":0.17629,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.50153,-0.02598,0.01602],"final_tcp_position":[0.50801,0.10161,0.28885],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273056.87969,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5016,-0.02596,0.01602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.33589,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":192.48197,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5205.0,"raw_peak_contact_force":1407.24694,"subtask_id":"reach_pre_grasp","tcp_end":[0.42448,-0.0074,0.18098],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18304,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50153,-0.02598,0.01602],"object_pos_start":[0.5016,-0.02596,0.01602],"object_to_goal_dist_end":0.33592,"object_to_goal_dist_start":0.33589,"object_z_max":0.01604,"peak_contact_force":373.7931,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5072.0,"raw_peak_contact_force":848.51782,"tcp_end":[0.45019,-0.01629,0.21689],"tcp_start":[0.42448,-0.0074,0.18098],"tcp_to_object_dist_end":0.20755,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":100.0,"n_steps_budget":50.0,"object_pos_end":[0.50153,-0.02598,0.01602],"object_pos_start":[0.50153,-0.02598,0.01602],"object_to_goal_dist_end":0.33592,"object_to_goal_dist_start":0.33592,"object_z_max":0.01602,"peak_contact_force":273004.12077,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3036.0,"raw_peak_contact_force":286.34584,"tcp_end":[0.45003,-0.01635,0.21606],"tcp_start":[0.45003,-0.01634,0.21606],"tcp_to_object_dist_end":0.20679,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1912.0,"n_steps_budget":1000.0,"object_pos_end":[0.50153,-0.02598,0.01602],"object_pos_start":[0.50153,-0.02598,0.01602],"object_to_goal_dist_end":0.33592,"object_to_goal_dist_start":0.33592,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15738.0,"raw_peak_contact_force":93.54647,"tcp_end":[0.43393,-0.01862,0.40749],"tcp_start":[0.44653,-0.01656,0.27361],"tcp_to_object_dist_end":0.39733,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50153,-0.02598,0.01602],"object_pos_start":[0.50153,-0.02598,0.01602],"object_to_goal_dist_end":0.33592,"object_to_goal_dist_start":0.33592,"object_z_max":0.01602,"peak_contact_force":273056.87969,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8286.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.49128,0.06818,0.29658],"tcp_start":[0.43393,-0.01862,0.40749],"tcp_to_object_dist_end":0.29611,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":185.0,"n_steps_budget":1000.0,"object_pos_end":[0.50153,-0.02598,0.01602],"object_pos_start":[0.50153,-0.02598,0.01602],"object_to_goal_dist_end":0.33592,"object_to_goal_dist_start":0.33592,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1537.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50702,0.09334,0.2755],"tcp_start":[0.49128,0.06818,0.29658],"tcp_to_object_dist_end":0.28565,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50153,-0.02598,0.01602],"object_pos_start":[0.50153,-0.02598,0.01602],"object_to_goal_dist_end":0.33592,"object_to_goal_dist_start":0.33592,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50515,0.09576,0.28476],"tcp_start":[0.50702,0.09334,0.2755],"tcp_to_object_dist_end":0.29505,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":16.0,"n_steps_budget":1000.0,"object_pos_end":[0.50153,-0.02598,0.01602],"object_pos_start":[0.50153,-0.02598,0.01602],"object_to_goal_dist_end":0.33592,"object_to_goal_dist_start":0.33592,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":64.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50801,0.10161,0.28885],"tcp_start":[0.50515,0.09576,0.28476],"tcp_to_object_dist_end":0.30126,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```