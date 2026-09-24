## Search State

- **Seed**: 5
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | -0.3280 | 0.21 | ❌ rejected |
| 2 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ✅ accepted |
| 1 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 0 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ✅ accepted |

**Proposal policy**: task_score is 0.21 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`
- Frozen object start: [0.530500292374538, 0.030794078973649372, 0.03]
- Frozen task target: [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]
- Goal object position: (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.530500292374538, 0.030794078973649372, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
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
  frozen_object_start: [0.5305, 0.0308, 0.03]
  frozen_task_target: [0.6015, 0.1786, 0.1081]
  frozen_object_starts: {'grasp_target': [0.530500292374538, 0.030794078973649372, 0.03]}
  frozen_targets: {'place_target': [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d

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
| `object` | offset from object initial position (0.530500292374538, 0.030794078973649372, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6015325561042142, 0.17858013800881417, 0.10808960535724847) | final destination targets |
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

## Current Skill (Q=-0.328) — your mutation base

```yaml
skill: grasp_place
skill_type: arm_gripper
phases:
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: release_1
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
- id: pull_1
  type: pull
  generator: arc_cartesian
  control: impedance_control
  termination: time_limit
  parameters:
    pull_angle:
      type: angle
      range:
      - 0.1
      - 1.2
    pull_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: release_2
  type: release
  control: position_control
  termination: pose_tolerance
  end_effector_action: open
- id: release_3
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  parameters:
    grip_force:
      type: scalar
      range:
      - 5.0
      - 30.0
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
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: -0.328
- **task_score** (E): 0.209
- **fitness_score**: 0.202  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.530

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_obj | 0.00 | 1.00 | 0.1276 |
| descend_grasp | 0.00 | 1.00 | 0.0567 |
| grasp_1 | 1.00 | 1.00 | 0.0000 |
| lift_1 | 1.00 | 1.00 | 0.1195 |
| approach_goal | 0.00 | 1.00 | 0.0850 |
| descend_place | 0.00 | 1.00 | 0.0311 |
| release_1 | 1.00 | 1.00 | 0.0246 |
| retract_1 | 0.00 | 1.00 | 0.0004 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_obj | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.438, 0.011, 0.191) | (0.516, 0.018, 0.030)→(0.498, 0.022, 0.023) | 0.234→0.243 | 1.00 / 5.000 | 199.520 | 1345.547 |
| descend_grasp | descend | 0.00 / step_budget | (0.438, 0.011, 0.191)→(0.464, 0.027, 0.159) | (0.498, 0.022, 0.023)→(0.498, 0.022, 0.023) | 0.243→0.243 | 1.00 / 5.000 | 394.967 | 996.486 |
| grasp_1 | grasp | 1.00 / step_budget | (0.464, 0.027, 0.157)→(0.464, 0.027, 0.157) | (0.498, 0.022, 0.023)→(0.498, 0.022, 0.023) | 0.243→0.243 | 1.00 / 9.000 | 74.073 | 207.362 |
| lift_1 | lift | 1.00 / step_budget | (0.464, 0.027, 0.157)→(0.464, 0.026, 0.277) | (0.498, 0.022, 0.023)→(0.498, 0.022, 0.023) | 0.243→0.243 | 1.00 / 8.000 | 3249.803 | 186.668 |
| approach_goal | approach | 0.00 / step_budget | (0.464, 0.026, 0.277)→(0.516, 0.089, 0.279) | (0.498, 0.022, 0.023)→(0.498, 0.022, 0.023) | 0.243→0.243 | 1.00 / 9.000 | 177.881 | 237.289 |
| descend_place | descend | 0.00 / step_budget | (0.516, 0.089, 0.279)→(0.522, 0.111, 0.258) | (0.498, 0.022, 0.023)→(0.498, 0.022, 0.023) | 0.243→0.243 | 1.00 / 9.333 | 327.904 | 446.210 |
| release_1 | release | 1.00 / step_budget | (0.522, 0.111, 0.258)→(0.524, 0.112, 0.283) | (0.498, 0.022, 0.023)→(0.498, 0.022, 0.023) | 0.243→0.243 | 1.00 / 6.000 | 234.130 | 322.164 |
| retract_1 | retract | 0.00 / step_budget | (0.524, 0.112, 0.283)→(0.524, 0.112, 0.283) | (0.498, 0.022, 0.023)→(0.498, 0.022, 0.023) | 0.243→0.243 | 1.00 / 6.000 | 246.053 | 258.175 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.265
- phase_score: 0.084
- phase_breakdown.reach_goal_score: 0.019
- phase_breakdown.reach_object_score: 0.182
- grasp_place_fitness: 0.228

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.228
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.265
- **Median Q (composite search score)**: -0.315
- **K-run variance**: 0.0008
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.405


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `181fdad61feb8a6d3dd6561c82dc2730a5598964bf30fa08b43615687239c379`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `eed1fc17ff57094d5189888f0dc8540ea7c165c4c73333e7487a550c7ded377e`; realized-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":82.0,"average_failure_rate":0.4385,"average_mean_iterations":91.48663,"average_solve_count":187.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.19091,"approach_goal.approach_speed":0.08018,"approach_obj.approach_height":0.09861,"descend_grasp.grasp_height":0.05984,"descend_place.place_z_offset":0.00614,"lift_1.lift_height":0.14841,"retract_1.retract_goal_z":0.1378},"optimized_scores":{"best_composite_score":-0.30198,"best_fitness_score":0.22802,"best_task_score":0.26518},"replay_outcomes":[{"contacts":{"omitted_contact_groups":11,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.53706,0.00791,-0.00347],"force_p95":212.67525,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1352.07476,"mean_force":66.76171,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.38731,0.00385,0.04555]},{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.64618,0.00829,-0.00044],"force_p95":214.56813,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1348.45531,"mean_force":200.76025,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.41779,0.00787,0.14117]},{"body_a":"world","body_b":"link6","contact_count":973.0,"contact_point_centroid":[0.63224,0.02328,-0.00022],"force_p95":485.31114,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1151.81072,"mean_force":310.26564,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.4412,0.02961,0.20159]},{"body_a":"link5","body_b":"hand","contact_count":272.0,"contact_point_centroid":[0.54788,0.03195,0.26665],"force_p95":335.76828,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":347.47721,"mean_force":285.06417,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51201,0.10569,0.27457]},{"body_a":"link5","body_b":"hand","contact_count":2.0,"contact_point_centroid":[0.54269,0.03894,0.22599],"force_p95":238.91616,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":242.05496,"mean_force":210.667,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52561,0.1126,0.27837]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.54263,0.03945,0.22682],"force_p95":214.53686,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":235.32503,"mean_force":163.33173,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5264,0.11242,0.28082]},{"body_a":"link5","body_b":"hand","contact_count":2.0,"contact_point_centroid":[0.54575,0.04074,0.24702],"force_p95":201.46832,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":206.14184,"mean_force":159.40662,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52687,0.11278,0.30099]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.68657,0.04061,-8e-05],"force_p95":190.15352,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":191.55683,"mean_force":148.70461,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46381,0.05379,0.15731]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.68647,0.04061,-0.00012],"force_p95":70.24114,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":161.05672,"mean_force":68.41043,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46382,0.05375,0.15738]},{"body_a":"grasp_target","body_b":"link7","contact_count":220.0,"contact_point_centroid":[0.50778,0.01482,0.03426],"force_p95":3.74881,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.76789,"mean_force":0.68353,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.39915,0.00441,0.09126]},{"body_a":"grasp_target","body_b":"hand","contact_count":193.0,"contact_point_centroid":[0.49892,0.0188,0.04883],"force_p95":2.21341,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.53206,"mean_force":0.67233,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.39837,0.00432,0.0881]},{"body_a":"world","body_b":"grasp_target","contact_count":3526.0,"contact_point_centroid":[0.49975,0.03902,-0.00258],"force_p95":0.4303,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.58001,"mean_force":0.17735,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.43074,0.00768,0.15437]},{"body_a":"grasp_target","body_b":"link6","contact_count":28.0,"contact_point_centroid":[0.54439,0.03058,0.00487],"force_p95":0.61506,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.6851,"mean_force":0.42621,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.38729,0.00389,0.05446]},{"body_a":"left_finger","body_b":"link5","contact_count":2.0,"contact_point_centroid":[0.51645,0.07386,0.28034],"force_p95":0.22412,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.22499,"mean_force":0.21624,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52687,0.11278,0.30099]},{"body_a":"left_finger","body_b":"link5","contact_count":8.0,"contact_point_centroid":[0.51641,0.07388,0.27898],"force_p95":0.15403,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.15517,"mean_force":0.14926,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52687,0.11277,0.29948]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.49111,0.04084,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.44173,0.02997,0.20117]}],"total_contact_groups":27},"final_pose_error":0.11375,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.49111,0.04084,0.01602],"final_tcp_position":[0.52684,0.11293,0.30111],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1352.07476,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49111,0.04084,0.01602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.1991,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":194.33389,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4878.0,"raw_peak_contact_force":1352.07476,"subtask_id":"reach_object","tcp_end":[0.44692,0.01443,0.19643],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18761,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49111,0.04084,0.01602],"object_pos_start":[0.49111,0.04084,0.01602],"object_to_goal_dist_end":0.1991,"object_to_goal_dist_start":0.1991,"object_z_max":0.01602,"peak_contact_force":352.00518,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4973.0,"raw_peak_contact_force":1151.81072,"subtask_id":"reach_object","tcp_end":[0.46387,0.05359,0.15785],"tcp_start":[0.44692,0.01443,0.19643],"tcp_to_object_dist_end":0.14499,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.49111,0.04084,0.01602],"object_pos_start":[0.49111,0.04084,0.01602],"object_to_goal_dist_end":0.1991,"object_to_goal_dist_start":0.1991,"object_z_max":0.01602,"peak_contact_force":85.25097,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3534.0,"raw_peak_contact_force":161.05672,"tcp_end":[0.4638,0.05378,0.15728],"tcp_start":[0.4638,0.05378,0.15728],"tcp_to_object_dist_end":0.14445,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":426.0,"n_steps_budget":930.0,"object_pos_end":[0.49111,0.04084,0.01602],"object_pos_start":[0.49111,0.04084,0.01602],"object_to_goal_dist_end":0.1991,"object_to_goal_dist_start":0.1991,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3550.0,"raw_peak_contact_force":191.55683,"subtask_id":"reach_goal","tcp_end":[0.46309,0.0537,0.28597],"tcp_start":[0.4638,0.05378,0.15728],"tcp_to_object_dist_end":0.27171,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":727.0,"n_steps_budget":1000.0,"object_pos_end":[0.49111,0.04084,0.01602],"object_pos_start":[0.49111,0.04084,0.01602],"object_to_goal_dist_end":0.1991,"object_to_goal_dist_start":0.1991,"object_z_max":0.01602,"peak_contact_force":264.42975,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6342.0,"raw_peak_contact_force":347.47721,"subtask_id":"reach_goal","tcp_end":[0.5255,0.11267,0.27826],"tcp_start":[0.46309,0.0537,0.28597],"tcp_to_object_dist_end":0.27406,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.49111,0.04084,0.01602],"object_pos_start":[0.49111,0.04084,0.01602],"object_to_goal_dist_end":0.1991,"object_to_goal_dist_start":0.1991,"object_z_max":0.01602,"peak_contact_force":252.58788,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":19.0,"raw_peak_contact_force":242.05496,"subtask_id":"reach_goal","tcp_end":[0.52579,0.11253,0.27849],"tcp_start":[0.5255,0.11267,0.27826],"tcp_to_object_dist_end":0.27428,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49111,0.04084,0.01602],"object_pos_start":[0.49111,0.04084,0.01602],"object_to_goal_dist_end":0.1991,"object_to_goal_dist_start":0.1991,"object_z_max":0.01602,"peak_contact_force":159.06512,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1234.0,"raw_peak_contact_force":235.32503,"tcp_end":[0.52687,0.11278,0.30088],"tcp_start":[0.52579,0.11253,0.27849],"tcp_to_object_dist_end":0.29597,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":2.0,"n_steps_budget":720.0,"object_pos_end":[0.49111,0.04084,0.01602],"object_pos_start":[0.49111,0.04084,0.01602],"object_to_goal_dist_end":0.1991,"object_to_goal_dist_start":0.1991,"object_z_max":0.01602,"peak_contact_force":207.82383,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":12.0,"raw_peak_contact_force":206.14184,"tcp_end":[0.52684,0.11293,0.30111],"tcp_start":[0.52687,0.11278,0.30088],"tcp_to_object_dist_end":0.29623,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5dcdc1a4e2a8d4c3bb30f9ac92fb306bea0b16a8f449f4d02b0333754e50f910`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":49.0,"average_failure_rate":0.28324,"average_mean_iterations":62.04624,"average_solve_count":173.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.19479,"approach_goal.approach_speed":0.06397,"approach_obj.approach_height":0.13727,"descend_grasp.grasp_height":0.02823,"descend_place.place_z_offset":-0.0044,"lift_1.lift_height":0.16801,"retract_1.retract_goal_z":0.142},"optimized_scores":{"best_composite_score":-0.36707,"best_fitness_score":0.16293,"best_task_score":0.12318},"replay_outcomes":[{"contacts":{"omitted_contact_groups":11,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.64001,-0.00481,-0.00044],"force_p95":205.60397,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1330.79128,"mean_force":199.29548,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.40763,-0.00473,0.13577]},{"body_a":"world","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.53222,0.00074,-0.00319],"force_p95":287.15546,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1269.81992,"mean_force":69.08181,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.38106,-0.00245,0.04679]},{"body_a":"world","body_b":"link6","contact_count":971.0,"contact_point_centroid":[0.6317,-0.00849,-0.00022],"force_p95":476.29411,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":947.71921,"mean_force":298.54284,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.43793,-0.01366,0.19666]},{"body_a":"link5","body_b":"hand","contact_count":49.0,"contact_point_centroid":[0.54622,0.02689,0.23533],"force_p95":766.43131,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":838.20056,"mean_force":592.42128,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.51682,0.10646,0.26137]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.54162,0.04291,0.21511],"force_p95":411.99395,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":456.98061,"mean_force":334.06134,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52515,0.1167,0.26244]},{"body_a":"link5","body_b":"hand","contact_count":5.0,"contact_point_centroid":[0.54505,0.04514,0.23558],"force_p95":331.89403,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":332.76062,"mean_force":290.36685,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52602,0.11794,0.2831]},{"body_a":"link5","body_b":"hand","contact_count":77.0,"contact_point_centroid":[0.53738,0.04391,0.17561],"force_p95":150.81313,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":233.95139,"mean_force":51.75114,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4651,-0.0427,0.15557]},{"body_a":"world","body_b":"link6","contact_count":545.0,"contact_point_centroid":[0.68742,-0.01103,-0.00013],"force_p95":82.35283,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":207.57064,"mean_force":70.94835,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46489,-0.04265,0.15489]},{"body_a":"world","body_b":"link6","contact_count":6.0,"contact_point_centroid":[0.68743,-0.01116,-0.0001],"force_p95":194.49631,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":197.08297,"mean_force":135.78796,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46487,-0.04284,0.15489]},{"body_a":"grasp_target","body_b":"link7","contact_count":572.0,"contact_point_centroid":[0.49939,-0.0203,0.0454],"force_p95":0.99353,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.94643,"mean_force":0.34827,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.40025,-0.00359,0.11782]},{"body_a":"grasp_target","body_b":"hand","contact_count":375.0,"contact_point_centroid":[0.49251,-0.03177,0.05508],"force_p95":2.02045,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.31639,"mean_force":0.491,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.396,-0.00298,0.10409]},{"body_a":"world","body_b":"grasp_target","contact_count":2772.0,"contact_point_centroid":[0.49142,-0.01689,-0.003],"force_p95":0.32868,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.38881,"mean_force":0.20651,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.42492,-0.00464,0.15232]},{"body_a":"left_finger","body_b":"link5","contact_count":5.0,"contact_point_centroid":[0.51655,0.08034,0.26701],"force_p95":0.54128,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.55709,"mean_force":0.46707,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52602,0.11794,0.2831]},{"body_a":"left_finger","body_b":"link5","contact_count":52.0,"contact_point_centroid":[0.51598,0.07991,0.25926],"force_p95":0.51202,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.52319,"mean_force":0.46516,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52579,0.11752,0.27469]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.49717,-0.01573,-0.002],"force_p95":0.13042,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15185,"mean_force":0.12298,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.43859,-0.0139,0.19633]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.49715,-0.01574,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4649,-0.04264,0.15492]}],"total_contact_groups":27},"final_pose_error":0.14127,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.49715,-0.01574,0.02602],"final_tcp_position":[0.52586,0.1183,0.28311],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1330.79128,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49728,-0.01572,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31407,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":193.19169,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4629.0,"raw_peak_contact_force":1330.79128,"subtask_id":"reach_object","tcp_end":[0.43056,-0.0084,0.18357],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17125,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49715,-0.01574,0.02602],"object_pos_start":[0.49728,-0.01572,0.02602],"object_to_goal_dist_end":0.31412,"object_to_goal_dist_start":0.31407,"object_z_max":0.02603,"peak_contact_force":391.711,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5065.0,"raw_peak_contact_force":947.71921,"subtask_id":"reach_object","tcp_end":[0.46505,-0.04072,0.15832],"tcp_start":[0.43056,-0.0084,0.18357],"tcp_to_object_dist_end":0.13841,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.49715,-0.01574,0.02602],"object_pos_start":[0.49715,-0.01574,0.02602],"object_to_goal_dist_end":0.31412,"object_to_goal_dist_start":0.31412,"object_z_max":0.02602,"peak_contact_force":67.94622,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3610.0,"raw_peak_contact_force":233.95139,"tcp_end":[0.46487,-0.04265,0.15478],"tcp_start":[0.46487,-0.04265,0.15478],"tcp_to_object_dist_end":0.13545,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":482.0,"n_steps_budget":1000.0,"object_pos_end":[0.49715,-0.01574,0.02602],"object_pos_start":[0.49715,-0.01574,0.02602],"object_to_goal_dist_end":0.31412,"object_to_goal_dist_start":0.31412,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4036.0,"raw_peak_contact_force":197.08297,"subtask_id":"reach_goal","tcp_end":[0.46434,-0.04282,0.30307],"tcp_start":[0.46487,-0.04265,0.15478],"tcp_to_object_dist_end":0.2803,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49715,-0.01574,0.02602],"object_pos_start":[0.49715,-0.01574,0.02602],"object_to_goal_dist_end":0.31412,"object_to_goal_dist_start":0.31412,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8450.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.50302,0.05213,0.31671],"tcp_start":[0.46434,-0.04282,0.30307],"tcp_to_object_dist_end":0.29856,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":118.0,"n_steps_budget":1000.0,"object_pos_end":[0.49715,-0.01574,0.02602],"object_pos_start":[0.49715,-0.01574,0.02602],"object_to_goal_dist_end":0.31412,"object_to_goal_dist_start":0.31412,"object_z_max":0.02602,"peak_contact_force":458.59506,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1037.0,"raw_peak_contact_force":838.20056,"subtask_id":"reach_goal","tcp_end":[0.52133,0.11851,0.25461],"tcp_start":[0.50302,0.05213,0.31671],"tcp_to_object_dist_end":0.26619,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49715,-0.01574,0.02602],"object_pos_start":[0.49715,-0.01574,0.02602],"object_to_goal_dist_end":0.31412,"object_to_goal_dist_start":0.31412,"object_z_max":0.02602,"peak_contact_force":313.23338,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1280.0,"raw_peak_contact_force":456.98061,"tcp_end":[0.52609,0.11792,0.28275],"tcp_start":[0.52133,0.11851,0.25461],"tcp_to_object_dist_end":0.29089,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":5.0,"n_steps_budget":900.0,"object_pos_end":[0.49715,-0.01574,0.02602],"object_pos_start":[0.49715,-0.01574,0.02602],"object_to_goal_dist_end":0.31412,"object_to_goal_dist_start":0.31412,"object_z_max":0.02602,"peak_contact_force":283.55017,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":30.0,"raw_peak_contact_force":332.76062,"tcp_end":[0.52586,0.1183,0.28311],"tcp_start":[0.52609,0.11792,0.28275],"tcp_to_object_dist_end":0.29135,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `53da4dc33bcb1151bde99c46f4ec5d44dda63d23acc62ec623c12d4d0fb32574`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":79.0,"average_failure_rate":0.48466,"average_mean_iterations":100.38037,"average_solve_count":163.0,"average_success_count":84.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.12692,"approach_goal.approach_speed":0.12132,"approach_obj.approach_height":0.15131,"descend_grasp.grasp_height":0.03915,"descend_place.place_z_offset":-0.01823,"lift_1.lift_height":0.10133,"retract_1.retract_goal_z":0.15865},"optimized_scores":{"best_composite_score":-0.31486,"best_fitness_score":0.21514,"best_task_score":0.2373},"replay_outcomes":[{"contacts":{"omitted_contact_groups":12,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.6437,0.01458,-0.00044],"force_p95":223.3858,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1353.7737,"mean_force":208.8658,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.41211,0.01396,0.13614]},{"body_a":"world","body_b":"link6","contact_count":970.0,"contact_point_centroid":[0.6275,0.03181,-0.00022],"force_p95":529.69364,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":889.92839,"mean_force":318.89321,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.43776,0.03975,0.20276]},{"body_a":"link5","body_b":"hand","contact_count":149.0,"contact_point_centroid":[0.54371,0.02405,0.23087],"force_p95":345.99631,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":364.2666,"mean_force":285.60298,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51142,0.10232,0.23782]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.53852,0.02364,0.20605],"force_p95":229.13556,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":274.18667,"mean_force":193.59475,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51894,0.10354,0.24392]},{"body_a":"link5","body_b":"hand","contact_count":2.0,"contact_point_centroid":[0.53862,0.02209,0.20506],"force_p95":257.4498,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":258.37404,"mean_force":249.13163,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5189,0.10263,0.24172]},{"body_a":"link5","body_b":"hand","contact_count":2.0,"contact_point_centroid":[0.54241,0.02685,0.22663],"force_p95":231.97324,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":235.62224,"mean_force":199.13228,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51987,0.10505,0.26428]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.68261,0.03395,-0.00012],"force_p95":72.54416,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":227.07861,"mean_force":70.01964,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4642,0.06867,0.16001]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.68269,0.03398,-0.0001],"force_p95":171.16212,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":171.36373,"mean_force":134.68125,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46419,0.06868,0.15994]},{"body_a":"world","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.53433,0.01165,-0.0034],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":111.46638,"mean_force":4.64443,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.38461,0.00701,0.04574]},{"body_a":"grasp_target","body_b":"link7","contact_count":545.0,"contact_point_centroid":[0.50359,0.02623,0.04499],"force_p95":0.94255,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.5805,"mean_force":0.35628,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.40384,0.01041,0.11542]},{"body_a":"grasp_target","body_b":"hand","contact_count":355.0,"contact_point_centroid":[0.49751,0.02297,0.056],"force_p95":1.94566,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.99243,"mean_force":0.43756,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.39937,0.00876,0.1016]},{"body_a":"world","body_b":"grasp_target","contact_count":2796.0,"contact_point_centroid":[0.50027,0.04221,-0.00304],"force_p95":0.35043,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.60492,"mean_force":0.20927,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.42915,0.0139,0.15334]},{"body_a":"left_finger","body_b":"link5","contact_count":2.0,"contact_point_centroid":[0.51197,0.06455,0.25297],"force_p95":0.44976,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.44987,"mean_force":0.44883,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51987,0.10505,0.26428]},{"body_a":"left_finger","body_b":"link5","contact_count":42.0,"contact_point_centroid":[0.51151,0.06402,0.24666],"force_p95":0.44211,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.44354,"mean_force":0.415,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51958,0.10456,0.25765]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50527,0.04053,-0.00202],"force_p95":0.16621,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18216,"mean_force":0.12449,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.43835,0.04016,0.20235]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.50518,0.04056,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4642,0.06867,0.16001]}],"total_contact_groups":28},"final_pose_error":0.13299,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.50518,0.04056,0.02602],"final_tcp_position":[0.51982,0.1052,0.2644],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":273004.12079,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50564,0.04037,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21562,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":211.0342,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4606.0,"raw_peak_contact_force":1353.7737,"subtask_id":"reach_object","tcp_end":[0.43748,0.02622,0.19159],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17962,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50518,0.04056,0.02602],"object_pos_start":[0.50564,0.04037,0.02602],"object_to_goal_dist_end":0.21576,"object_to_goal_dist_start":0.21562,"object_z_max":0.02604,"peak_contact_force":441.18551,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5158.0,"raw_peak_contact_force":889.92839,"subtask_id":"reach_object","tcp_end":[0.46422,0.06896,0.16111],"tcp_start":[0.43748,0.02622,0.19159],"tcp_to_object_dist_end":0.14399,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50518,0.04056,0.02602],"object_pos_start":[0.50518,0.04056,0.02602],"object_to_goal_dist_end":0.21576,"object_to_goal_dist_start":0.21576,"object_z_max":0.02602,"peak_contact_force":69.0221,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3529.0,"raw_peak_contact_force":227.07861,"tcp_end":[0.46418,0.06866,0.1599],"tcp_start":[0.46418,0.06866,0.1599],"tcp_to_object_dist_end":0.14281,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":265.0,"n_steps_budget":660.0,"object_pos_end":[0.50518,0.04056,0.02602],"object_pos_start":[0.50518,0.04056,0.02602],"object_to_goal_dist_end":0.21576,"object_to_goal_dist_start":0.21576,"object_z_max":0.02602,"peak_contact_force":9749.16355,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2236.0,"raw_peak_contact_force":171.36373,"subtask_id":"reach_goal","tcp_end":[0.46317,0.0684,0.24139],"tcp_start":[0.46418,0.06866,0.1599],"tcp_to_object_dist_end":0.22119,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":444.0,"n_steps_budget":1000.0,"object_pos_end":[0.50518,0.04056,0.02602],"object_pos_start":[0.50518,0.04056,0.02602],"object_to_goal_dist_end":0.21576,"object_to_goal_dist_start":0.21576,"object_z_max":0.02602,"peak_contact_force":269.08962,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3876.0,"raw_peak_contact_force":364.2666,"subtask_id":"reach_goal","tcp_end":[0.51884,0.10264,0.24174],"tcp_start":[0.46317,0.0684,0.24139],"tcp_to_object_dist_end":0.22489,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.50518,0.04056,0.02602],"object_pos_start":[0.50518,0.04056,0.02602],"object_to_goal_dist_end":0.21576,"object_to_goal_dist_start":0.21576,"object_z_max":0.02602,"peak_contact_force":272.52778,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":19.0,"raw_peak_contact_force":258.37404,"subtask_id":"reach_goal","tcp_end":[0.51894,0.10269,0.24143],"tcp_start":[0.51884,0.10264,0.24174],"tcp_to_object_dist_end":0.22462,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50518,0.04056,0.02602],"object_pos_start":[0.50518,0.04056,0.02602],"object_to_goal_dist_end":0.21576,"object_to_goal_dist_start":0.21576,"object_z_max":0.02602,"peak_contact_force":230.09115,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1271.0,"raw_peak_contact_force":274.18667,"tcp_end":[0.51986,0.10504,0.26418],"tcp_start":[0.51894,0.10269,0.24143],"tcp_to_object_dist_end":0.24717,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":2.0,"n_steps_budget":840.0,"object_pos_end":[0.50518,0.04056,0.02602],"object_pos_start":[0.50518,0.04056,0.02602],"object_to_goal_dist_end":0.21576,"object_to_goal_dist_start":0.21576,"object_z_max":0.02602,"peak_contact_force":246.78564,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":12.0,"raw_peak_contact_force":235.62224,"tcp_end":[0.51982,0.1052,0.2644],"tcp_start":[0.51986,0.10504,0.26418],"tcp_to_object_dist_end":0.24742,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```