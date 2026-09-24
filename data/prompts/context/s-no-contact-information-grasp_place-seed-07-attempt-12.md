## Search State

- **Seed**: 7
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | -0.4799 | 0.15 | ❌ rejected |
| 11 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |
| 10 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |
| 9 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.5147 | 0.15 | ❌ rejected |

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
- Frozen object start: [0.5125095466604667, 0.039721380096957554, 0.03]
- Frozen task target: [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]
- Goal object position: (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5125095466604667, 0.039721380096957554, 0.03)
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
  frozen_object_start: [0.5125, 0.0397, 0.03]
  frozen_task_target: [0.6276, 0.1725, 0.145]
  frozen_object_starts: {'grasp_target': [0.5125095466604667, 0.039721380096957554, 0.03]}
  frozen_targets: {'place_target': [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]}
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
| `object` | offset from object initial position (0.5125095466604667, 0.039721380096957554, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6275685690245193, 0.17252071899905919, 0.14502494273668382) | final destination targets |
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

## Current Skill (Q=-0.480) — your mutation base

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

- **Composite score**: -0.480
- **task_score** (E): 0.145
- **fitness_score**: 0.150  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_object_1 | 0.00 | 0.1804 |
| descend_grasp_1 | 0.00 | 0.0312 |
| grasp_1 | 1.00 | 0.0000 |
| lift_1 | 0.67 | 0.0716 |
| approach_goal_1 | 0.00 | 0.1218 |
| descend_place_1 | 0.00 | 0.0177 |
| release_1 | 1.00 | 0.0234 |
| retract_final_1 | 0.00 | 0.0147 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_object_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.404, 0.010, 0.149) | (0.511, 0.022, 0.030)→(0.470, 0.025, 0.016) | 0.271→0.295 |
| descend_grasp_1 | descend | 0.00 / step_budget | (0.404, 0.010, 0.149)→(0.401, 0.017, 0.177) | (0.470, 0.025, 0.016)→(0.470, 0.025, 0.016) | 0.295→0.296 |
| grasp_1 | grasp | 1.00 / step_budget | (0.401, 0.017, 0.176)→(0.401, 0.017, 0.176) | (0.470, 0.025, 0.016)→(0.470, 0.025, 0.016) | 0.296→0.296 |
| lift_1 | lift | 0.67 / step_budget | (0.401, 0.017, 0.176)→(0.462, 0.012, 0.200) | (0.470, 0.025, 0.016)→(0.470, 0.025, 0.016) | 0.296→0.296 |
| approach_goal_1 | approach | 0.00 / step_budget | (0.462, 0.012, 0.200)→(0.522, 0.085, 0.275) | (0.470, 0.025, 0.016)→(0.470, 0.025, 0.016) | 0.296→0.296 |
| descend_place_1 | descend | 0.00 / step_budget | (0.522, 0.085, 0.275)→(0.531, 0.098, 0.271) | (0.470, 0.025, 0.016)→(0.470, 0.025, 0.016) | 0.296→0.296 |
| release_1 | release | 1.00 / step_budget | (0.531, 0.098, 0.271)→(0.533, 0.099, 0.294) | (0.470, 0.025, 0.016)→(0.470, 0.025, 0.016) | 0.296→0.296 |
| retract_final_1 | retract | 0.00 / step_budget | (0.533, 0.099, 0.294)→(0.537, 0.103, 0.308) | (0.470, 0.025, 0.016)→(0.470, 0.025, 0.016) | 0.296→0.296 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.204
- phase_score: 0.071
- phase_breakdown.grasp_object_score: 0.038
- phase_breakdown.lift_object_score: 0.237
- phase_breakdown.approach_object_score: 0.102
- phase_breakdown.approach_goal_score: 0.023
- phase_breakdown.place_goal_score: 0.057
- grasp_place_fitness: 0.179

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.179
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.204
- **Median Q (composite search score)**: -0.483
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.424


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
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":221.0,"average_failure_rate":0.62606,"average_mean_iterations":127.67422,"average_solve_count":353.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal_1.transport_speed":0.0614,"approach_object_1.approach_speed":0.0398,"descend_grasp_1.descend_speed":0.01546,"descend_grasp_1.grasp_height":0.05701,"descend_place_1.place_height":0.03638,"descend_place_1.place_speed":0.02358,"lift_1.lift_height":0.14108,"lift_1.lift_speed":0.05175,"retract_final_1.retract_speed":0.08616},"optimized_scores":{"best_composite_score":-0.45109,"best_fitness_score":0.17891,"best_task_score":0.20419},"replay_outcomes":[{"contacts":{"omitted_contact_groups":10,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.63739,0.00876,-0.00049],"force_p95":197.45088,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1453.72593,"mean_force":200.84957,"phase_index":0.0,"phase_name":"approach_object_1","phase_type":"approach","tcp_position_centroid":[0.39663,0.00824,0.12399]},{"body_a":"world","body_b":"link6","contact_count":552.0,"contact_point_centroid":[0.6404,0.02214,-0.00018],"force_p95":476.29097,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":903.51312,"mean_force":287.96521,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44547,0.03058,0.20016]},{"body_a":"link5","body_b":"hand","contact_count":173.0,"contact_point_centroid":[0.52795,-0.0068,0.17193],"force_p95":389.23936,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":471.50116,"mean_force":305.09214,"phase_index":4.0,"phase_name":"approach_goal_1","phase_type":"approach","tcp_position_centroid":[0.50055,0.07245,0.20517]},{"body_a":"link5","body_b":"hand","contact_count":6.0,"contact_point_centroid":[0.52397,0.01818,0.15712],"force_p95":291.50821,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":294.14919,"mean_force":272.53627,"phase_index":5.0,"phase_name":"descend_place_1","phase_type":"descend","tcp_position_centroid":[0.51718,0.08986,0.21731]},{"body_a":"link5","body_b":"hand","contact_count":8.0,"contact_point_centroid":[0.53034,0.02495,0.18083],"force_p95":286.91599,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":288.88977,"mean_force":252.44189,"phase_index":7.0,"phase_name":"retract_final_1","phase_type":"retract","tcp_position_centroid":[0.52109,0.09123,0.24475]},{"body_a":"world","body_b":"link6","contact_count":14.0,"contact_point_centroid":[0.68573,0.03369,-8e-05],"force_p95":268.61767,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":277.52893,"mean_force":172.25745,"phase_index":4.0,"phase_name":"approach_goal_1","phase_type":"approach","tcp_position_centroid":[0.46858,0.04173,0.17447]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.5246,0.02154,0.15955],"force_p95":245.3733,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":266.6132,"mean_force":219.36955,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51994,0.0892,0.2239]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.61802,0.01756,-0.00025],"force_p95":198.85861,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":257.26826,"mean_force":197.28054,"phase_index":1.0,"phase_name":"descend_grasp_1","phase_type":"descend","tcp_position_centroid":[0.3914,0.01943,0.151]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.60793,0.02268,-0.00014],"force_p95":82.92107,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":86.04421,"mean_force":74.4273,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.40013,0.0242,0.17695]},{"body_a":"world","body_b":"link6","contact_count":39.0,"contact_point_centroid":[0.66694,0.01823,-0.00014],"force_p95":80.41655,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":81.92771,"mean_force":35.51147,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51946,0.08869,0.21663]},{"body_a":"grasp_target","body_b":"link7","contact_count":278.0,"contact_point_centroid":[0.4956,0.0212,0.03674],"force_p95":1.37688,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.8129,"mean_force":0.51247,"phase_index":0.0,"phase_name":"approach_object_1","phase_type":"approach","tcp_position_centroid":[0.39048,0.0059,0.09857]},{"body_a":"grasp_target","body_b":"hand","contact_count":255.0,"contact_point_centroid":[0.48464,0.02317,0.05254],"force_p95":2.39741,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.62326,"mean_force":0.50537,"phase_index":0.0,"phase_name":"approach_object_1","phase_type":"approach","tcp_position_centroid":[0.39036,0.00583,0.09659]},{"body_a":"world","body_b":"grasp_target","contact_count":3371.0,"contact_point_centroid":[0.4807,0.04694,-0.0027],"force_p95":0.38361,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44152,"mean_force":0.18381,"phase_index":0.0,"phase_name":"approach_object_1","phase_type":"approach","tcp_position_centroid":[0.4111,0.00807,0.13767]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.46984,0.04895,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp_1","phase_type":"descend","tcp_position_centroid":[0.3914,0.01943,0.151]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.46984,0.04895,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.40013,0.0242,0.17695]},{"body_a":"world","body_b":"grasp_target","contact_count":2280.0,"contact_point_centroid":[0.46984,0.04895,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4459,0.03077,0.19977]}],"total_contact_groups":26},"final_pose_error":0.2404,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.46984,0.04895,0.01602],"final_tcp_position":[0.52143,0.09247,0.24472],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46984,0.04895,0.01602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.23831,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"phase_name":"approach_object_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.40515,0.01226,0.15203],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15501,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46984,0.04895,0.01602],"object_pos_start":[0.46984,0.04895,0.01602],"object_to_goal_dist_end":0.23831,"object_to_goal_dist_start":0.23831,"object_z_max":0.01602,"phase_name":"descend_grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_object","tcp_end":[0.39979,0.02421,0.17712],"tcp_start":[0.40515,0.01226,0.15203],"tcp_to_object_dist_end":0.1774,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.46984,0.04895,0.01602],"object_pos_start":[0.46984,0.04895,0.01602],"object_to_goal_dist_end":0.23831,"object_to_goal_dist_start":0.23831,"object_z_max":0.01602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.40019,0.02418,0.17684],"tcp_start":[0.40019,0.02418,0.17685],"tcp_to_object_dist_end":0.177,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":570.0,"n_steps_budget":930.0,"object_pos_end":[0.46984,0.04895,0.01602],"object_pos_start":[0.46984,0.04895,0.01602],"object_to_goal_dist_end":0.23831,"object_to_goal_dist_start":0.23831,"object_z_max":0.01602,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.46701,0.03933,0.17431],"tcp_start":[0.40019,0.02418,0.17684],"tcp_to_object_dist_end":0.15861,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":317.0,"n_steps_budget":1000.0,"object_pos_end":[0.46984,0.04895,0.01602],"object_pos_start":[0.46984,0.04895,0.01602],"object_to_goal_dist_end":0.23831,"object_to_goal_dist_start":0.23831,"object_z_max":0.01602,"phase_name":"approach_goal_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_goal","tcp_end":[0.51643,0.08969,0.2164],"tcp_start":[0.46701,0.03933,0.17431],"tcp_to_object_dist_end":0.20972,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.46984,0.04895,0.01602],"object_pos_start":[0.46984,0.04895,0.01602],"object_to_goal_dist_end":0.23831,"object_to_goal_dist_start":0.23831,"object_z_max":0.01602,"phase_name":"descend_place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.51812,0.09036,0.21797],"tcp_start":[0.51643,0.08969,0.2164],"tcp_to_object_dist_end":0.21173,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46984,0.04895,0.01602],"object_pos_start":[0.46984,0.04895,0.01602],"object_to_goal_dist_end":0.23831,"object_to_goal_dist_start":0.23831,"object_z_max":0.01602,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.52095,0.09096,0.24429],"tcp_start":[0.51812,0.09036,0.21797],"tcp_to_object_dist_end":0.23766,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":8.0,"n_steps_budget":1000.0,"object_pos_end":[0.46984,0.04895,0.01602],"object_pos_start":[0.46984,0.04895,0.01602],"object_to_goal_dist_end":0.23831,"object_to_goal_dist_start":0.23831,"object_z_max":0.01602,"phase_name":"retract_final_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.52143,0.09247,0.24472],"tcp_start":[0.52095,0.09096,0.24429],"tcp_to_object_dist_end":0.23846,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a74f7c08b88460953bfa7e35b953cddf9278fdc17d2d4db8a2ea121b328e8b73`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":57.0,"average_failure_rate":0.27941,"average_mean_iterations":59.91176,"average_solve_count":204.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal_1.transport_speed":0.12208,"approach_object_1.approach_speed":0.07722,"descend_grasp_1.descend_speed":0.01207,"descend_grasp_1.grasp_height":0.05862,"descend_place_1.place_height":0.09036,"descend_place_1.place_speed":0.03599,"lift_1.lift_height":0.18424,"lift_1.lift_speed":0.08599,"retract_final_1.retract_speed":0.11915},"optimized_scores":{"best_composite_score":-0.48286,"best_fitness_score":0.14714,"best_task_score":0.12486},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.63642,0.01436,-0.00046],"force_p95":209.51674,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1327.26418,"mean_force":206.99894,"phase_index":0.0,"phase_name":"approach_object_1","phase_type":"approach","tcp_position_centroid":[0.39423,0.01354,0.11987]},{"body_a":"world","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.52778,0.01258,-0.00317],"force_p95":277.49824,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1261.89529,"mean_force":68.27073,"phase_index":0.0,"phase_name":"approach_object_1","phase_type":"approach","tcp_position_centroid":[0.37683,0.00756,0.04732]},{"body_a":"link5","body_b":"hand","contact_count":153.0,"contact_point_centroid":[0.54476,0.06676,0.29216],"force_p95":312.69108,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":335.86071,"mean_force":268.58834,"phase_index":4.0,"phase_name":"approach_goal_1","phase_type":"approach","tcp_position_centroid":[0.5106,0.14532,0.31294]},{"body_a":"world","body_b":"link6","contact_count":8.0,"contact_point_centroid":[0.60865,0.03485,-0.0001],"force_p95":304.72618,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":309.29159,"mean_force":224.61431,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.39649,0.03802,0.17176]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.61809,0.02942,-0.00026],"force_p95":201.97476,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":302.59661,"mean_force":198.90262,"phase_index":1.0,"phase_name":"descend_grasp_1","phase_type":"descend","tcp_position_centroid":[0.38961,0.0325,0.14837]},{"body_a":"link5","body_b":"hand","contact_count":487.0,"contact_point_centroid":[0.54466,0.08491,0.26507],"force_p95":262.60696,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":278.17983,"mean_force":225.79281,"phase_index":5.0,"phase_name":"descend_place_1","phase_type":"descend","tcp_position_centroid":[0.52912,0.16557,0.3191]},{"body_a":"link5","body_b":"hand","contact_count":176.0,"contact_point_centroid":[0.54128,0.12003,0.23738],"force_p95":161.95661,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":170.23736,"mean_force":66.32303,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54517,0.18981,0.31331]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.60861,0.03483,-0.00014],"force_p95":83.93674,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":90.13976,"mean_force":74.31904,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.39616,0.03801,0.17132]},{"body_a":"grasp_target","body_b":"hand","contact_count":48.0,"contact_point_centroid":[0.45874,0.04408,0.04028],"force_p95":3.73041,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.10426,"mean_force":1.56586,"phase_index":0.0,"phase_name":"approach_object_1","phase_type":"approach","tcp_position_centroid":[0.38516,0.00766,0.05361]},{"body_a":"world","body_b":"grasp_target","contact_count":3891.0,"contact_point_centroid":[0.44752,0.05003,-0.00216],"force_p95":0.13841,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.55695,"mean_force":0.14013,"phase_index":0.0,"phase_name":"approach_object_1","phase_type":"approach","tcp_position_centroid":[0.40621,0.01278,0.13034]},{"body_a":"grasp_target","body_b":"link7","contact_count":33.0,"contact_point_centroid":[0.48972,0.02975,0.01028],"force_p95":0.87916,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.91352,"mean_force":0.39523,"phase_index":0.0,"phase_name":"approach_object_1","phase_type":"approach","tcp_position_centroid":[0.37737,0.00762,0.05394]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.44228,0.0502,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp_1","phase_type":"descend","tcp_position_centroid":[0.38961,0.0325,0.14837]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.44228,0.0502,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.39616,0.03801,0.17132]},{"body_a":"world","body_b":"grasp_target","contact_count":448.0,"contact_point_centroid":[0.44228,0.0502,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.41175,0.04216,0.17947]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.44228,0.0502,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"approach_goal_1","phase_type":"approach","tcp_position_centroid":[0.47843,0.11267,0.25404]},{"body_a":"world","body_b":"grasp_target","contact_count":1960.0,"contact_point_centroid":[0.44228,0.0502,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place_1","phase_type":"descend","tcp_position_centroid":[0.52916,0.16562,0.3191]}],"total_contact_groups":23},"final_pose_error":0.1608,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.44228,0.0502,0.01602],"final_tcp_position":[0.55537,0.19996,0.37453],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44228,0.0502,0.01602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.31208,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"phase_name":"approach_object_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.40385,0.02201,0.1503],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14249,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44228,0.0502,0.01602],"object_pos_start":[0.44228,0.0502,0.01602],"object_to_goal_dist_end":0.31208,"object_to_goal_dist_start":0.31208,"object_z_max":0.01602,"phase_name":"descend_grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_object","tcp_end":[0.3958,0.03801,0.1715],"tcp_start":[0.40385,0.02201,0.1503],"tcp_to_object_dist_end":0.16274,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.44228,0.0502,0.01602],"object_pos_start":[0.44228,0.0502,0.01602],"object_to_goal_dist_end":0.31208,"object_to_goal_dist_start":0.31208,"object_z_max":0.01602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.39622,0.03799,0.1712],"tcp_start":[0.39622,0.038,0.17121],"tcp_to_object_dist_end":0.16233,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":112.0,"n_steps_budget":600.0,"object_pos_end":[0.44228,0.0502,0.01602],"object_pos_start":[0.44228,0.0502,0.01602],"object_to_goal_dist_end":0.31208,"object_to_goal_dist_start":0.31208,"object_z_max":0.01602,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.42781,0.04655,0.1873],"tcp_start":[0.39622,0.03799,0.1712],"tcp_to_object_dist_end":0.17193,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44228,0.0502,0.01602],"object_pos_start":[0.44228,0.0502,0.01602],"object_to_goal_dist_end":0.31208,"object_to_goal_dist_start":0.31208,"object_z_max":0.01602,"phase_name":"approach_goal_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_goal","tcp_end":[0.51759,0.15069,0.32871],"tcp_start":[0.42781,0.04655,0.1873],"tcp_to_object_dist_end":0.33696,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":490.0,"n_steps_budget":1000.0,"object_pos_end":[0.44228,0.0502,0.01602],"object_pos_start":[0.44228,0.0502,0.01602],"object_to_goal_dist_end":0.31208,"object_to_goal_dist_start":0.31208,"object_z_max":0.01602,"phase_name":"descend_place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.54389,0.18988,0.31389],"tcp_start":[0.51759,0.15069,0.32871],"tcp_to_object_dist_end":0.34433,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.44228,0.0502,0.01602],"object_pos_start":[0.44228,0.0502,0.01602],"object_to_goal_dist_end":0.31208,"object_to_goal_dist_start":0.31208,"object_z_max":0.01602,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.54588,0.18988,0.33506],"tcp_start":[0.54389,0.18988,0.31389],"tcp_to_object_dist_end":0.36335,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":92.0,"n_steps_budget":1000.0,"object_pos_end":[0.44228,0.0502,0.01602],"object_pos_start":[0.44228,0.0502,0.01602],"object_to_goal_dist_end":0.31208,"object_to_goal_dist_start":0.31208,"object_z_max":0.01602,"phase_name":"retract_final_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.55537,0.19996,0.37453],"tcp_start":[0.54588,0.18988,0.33506],"tcp_to_object_dist_end":0.40466,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b1a72366a9c9a56aa2e80fc4399e157c8281abf492ab3c1ede02058762a86ed7`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":223.0,"average_failure_rate":0.64265,"average_mean_iterations":130.8732,"average_solve_count":347.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal_1.transport_speed":0.14592,"approach_object_1.approach_speed":0.02005,"descend_grasp_1.descend_speed":0.0119,"descend_grasp_1.grasp_height":0.05992,"descend_place_1.place_height":0.06131,"descend_place_1.place_speed":0.01645,"lift_1.lift_height":0.28696,"lift_1.lift_speed":0.08633,"retract_final_1.retract_speed":0.07701},"optimized_scores":{"best_composite_score":-0.50585,"best_fitness_score":0.12415,"best_task_score":0.10597},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.63929,-0.00356,-0.00047],"force_p95":194.52281,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1434.16188,"mean_force":198.25224,"phase_index":0.0,"phase_name":"approach_object_1","phase_type":"approach","tcp_position_centroid":[0.39644,-0.00363,0.12004]},{"body_a":"world","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.53393,0.00126,-0.00336],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":466.76391,"mean_force":22.22685,"phase_index":0.0,"phase_name":"approach_object_1","phase_type":"approach","tcp_position_centroid":[0.38017,-0.00272,0.04957]},{"body_a":"link5","body_b":"hand","contact_count":43.0,"contact_point_centroid":[0.54798,0.0564,0.2323],"force_p95":238.03026,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":247.90815,"mean_force":97.73789,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4891,-0.04411,0.24162]},{"body_a":"link5","body_b":"hand","contact_count":432.0,"contact_point_centroid":[0.54365,0.05823,0.21771],"force_p95":154.26521,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":236.39474,"mean_force":109.36983,"phase_index":4.0,"phase_name":"approach_goal_1","phase_type":"approach","tcp_position_centroid":[0.52287,-0.05122,0.22878]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.62185,-0.00716,-0.00025],"force_p95":195.13445,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":207.16362,"mean_force":192.83868,"phase_index":1.0,"phase_name":"descend_grasp_1","phase_type":"descend","tcp_position_centroid":[0.39591,-0.00859,0.15177]},{"body_a":"world","body_b":"link6","contact_count":7.0,"contact_point_centroid":[0.61128,-0.00993,-0.00011],"force_p95":188.10605,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":203.65163,"mean_force":129.78044,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.40701,-0.01105,0.18106]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.61119,-0.00987,-0.00014],"force_p95":81.54207,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":83.44577,"mean_force":74.14506,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.40681,-0.011,0.18088]},{"body_a":"grasp_target","body_b":"link7","contact_count":688.0,"contact_point_centroid":[0.52509,-0.01122,0.03252],"force_p95":0.78212,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.78781,"mean_force":0.26854,"phase_index":0.0,"phase_name":"approach_object_1","phase_type":"approach","tcp_position_centroid":[0.39532,-0.00331,0.11281]},{"body_a":"grasp_target","body_b":"hand","contact_count":116.0,"contact_point_centroid":[0.4939,-0.02845,0.04628],"force_p95":2.34165,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.24363,"mean_force":0.91916,"phase_index":0.0,"phase_name":"approach_object_1","phase_type":"approach","tcp_position_centroid":[0.38882,-0.00273,0.0803]},{"body_a":"grasp_target","body_b":"link6","contact_count":105.0,"contact_point_centroid":[0.54128,-0.02478,0.02681],"force_p95":0.83425,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.8185,"mean_force":0.43169,"phase_index":0.0,"phase_name":"approach_object_1","phase_type":"approach","tcp_position_centroid":[0.38659,-0.00273,0.08388]},{"body_a":"world","body_b":"grasp_target","contact_count":3751.0,"contact_point_centroid":[0.50577,-0.02415,-0.00242],"force_p95":0.28458,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.33413,"mean_force":0.16579,"phase_index":0.0,"phase_name":"approach_object_1","phase_type":"approach","tcp_position_centroid":[0.4092,-0.00344,0.13173]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.49768,-0.02503,-0.00206],"force_p95":0.15973,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17437,"mean_force":0.12772,"phase_index":1.0,"phase_name":"descend_grasp_1","phase_type":"descend","tcp_position_centroid":[0.39591,-0.00859,0.15177]},{"body_a":"grasp_target","body_b":"link6","contact_count":358.0,"contact_point_centroid":[0.52585,-0.008,0.03438],"force_p95":0.11279,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16284,"mean_force":0.08756,"phase_index":1.0,"phase_name":"descend_grasp_1","phase_type":"descend","tcp_position_centroid":[0.39053,-0.00719,0.13534]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.4973,-0.02514,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.40681,-0.011,0.18088]},{"body_a":"world","body_b":"grasp_target","contact_count":2380.0,"contact_point_centroid":[0.4973,-0.02514,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45654,-0.021,0.232]},{"body_a":"world","body_b":"grasp_target","contact_count":2584.0,"contact_point_centroid":[0.4973,-0.02514,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_goal_1","phase_type":"approach","tcp_position_centroid":[0.52557,-0.04098,0.2381]}],"total_contact_groups":25},"final_pose_error":0.30375,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.4973,-0.02514,0.01602],"final_tcp_position":[0.53325,0.01532,0.30443],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49925,-0.02446,0.01602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.33552,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"phase_name":"approach_object_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.40246,-0.00498,0.14407],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16169,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4973,-0.02514,0.01602],"object_pos_start":[0.49925,-0.02446,0.01602],"object_to_goal_dist_end":0.33669,"object_to_goal_dist_start":0.33552,"object_z_max":0.01603,"phase_name":"descend_grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_object","tcp_end":[0.40648,-0.01094,0.18105],"tcp_start":[0.40246,-0.00498,0.14407],"tcp_to_object_dist_end":0.18891,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.4973,-0.02514,0.01602],"object_pos_start":[0.4973,-0.02514,0.01602],"object_to_goal_dist_end":0.33669,"object_to_goal_dist_start":0.33669,"object_z_max":0.01602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.40686,-0.01103,0.18078],"tcp_start":[0.40686,-0.01103,0.18078],"tcp_to_object_dist_end":0.18848,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":595.0,"n_steps_budget":1000.0,"object_pos_end":[0.4973,-0.02514,0.01602],"object_pos_start":[0.4973,-0.02514,0.01602],"object_to_goal_dist_end":0.33669,"object_to_goal_dist_start":0.33669,"object_z_max":0.01602,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.4916,-0.05012,0.23878],"tcp_start":[0.40686,-0.01103,0.18078],"tcp_to_object_dist_end":0.22423,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":646.0,"n_steps_budget":1000.0,"object_pos_end":[0.4973,-0.02514,0.01602],"object_pos_start":[0.4973,-0.02514,0.01602],"object_to_goal_dist_end":0.33669,"object_to_goal_dist_start":0.33669,"object_z_max":0.01602,"phase_name":"approach_goal_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_goal","tcp_end":[0.53208,0.01328,0.28075],"tcp_start":[0.4916,-0.05012,0.23878],"tcp_to_object_dist_end":0.26975,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.4973,-0.02514,0.01602],"object_pos_start":[0.4973,-0.02514,0.01602],"object_to_goal_dist_end":0.33669,"object_to_goal_dist_start":0.33669,"object_z_max":0.01602,"phase_name":"descend_place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.53247,0.01422,0.28127],"tcp_start":[0.53208,0.01328,0.28075],"tcp_to_object_dist_end":0.27045,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4973,-0.02514,0.01602],"object_pos_start":[0.4973,-0.02514,0.01602],"object_to_goal_dist_end":0.33669,"object_to_goal_dist_start":0.33669,"object_z_max":0.01602,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.53302,0.01517,0.30382],"tcp_start":[0.53247,0.01422,0.28127],"tcp_to_object_dist_end":0.2928,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.4973,-0.02514,0.01602],"object_pos_start":[0.4973,-0.02514,0.01602],"object_to_goal_dist_end":0.33669,"object_to_goal_dist_start":0.33669,"object_z_max":0.01602,"phase_name":"retract_final_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.53325,0.01532,0.30443],"tcp_start":[0.53302,0.01517,0.30382],"tcp_to_object_dist_end":0.29344,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```