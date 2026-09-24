## Search State

- **Seed**: 7
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.5147 | 0.15 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.5365 | 0.17 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.3909 | 0.18 | ❌ rejected |
| 5 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | -0.0468 | 0.17 | ❌ rejected |

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

## Current Skill (Q=-0.515) — your mutation base

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

- **Composite score**: -0.515
- **task_score** (E): 0.151
- **fitness_score**: 0.215  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.730

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_to_object | 1.00 | 0.0786 |
| descend_to_object | 0.00 | 0.1636 |
| grasp_object | 0.00 | 0.0000 |
| lift_object | 1.00 | 0.0110 |
| approach_to_goal | 0.00 | 0.1241 |
| descend_to_goal | 0.00 | 0.0913 |
| release_at_goal | 1.00 | 0.0276 |
| retract_from_goal | 1.00 | 0.0995 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_to_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.017, 0.230) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 |
| descend_to_object | descend | 0.00 / step_budget | (0.506, 0.017, 0.230)→(0.455, 0.047, 0.095) | (0.511, 0.022, 0.026)→(0.462, 0.043, 0.016) | 0.273→0.293 |
| grasp_object | grasp | 0.00 / guard_failure | (0.456, 0.046, 0.094)→(0.456, 0.046, 0.094) | (0.462, 0.043, 0.016)→(0.462, 0.043, 0.016) | 0.293→0.293 |
| lift_object | lift | 1.00 / step_budget | (0.459, 0.045, 0.155)→(0.459, 0.044, 0.166) | (0.462, 0.043, 0.016)→(0.462, 0.043, 0.016) | 0.293→0.293 |
| approach_to_goal | approach | 0.00 / step_budget | (0.459, 0.044, 0.166)→(0.531, 0.105, 0.238) | (0.462, 0.043, 0.016)→(0.462, 0.043, 0.016) | 0.293→0.293 |
| descend_to_goal | descend | 0.00 / step_budget | (0.531, 0.105, 0.238)→(0.563, 0.148, 0.291) | (0.462, 0.043, 0.016)→(0.462, 0.043, 0.016) | 0.293→0.293 |
| release_at_goal | release | 1.00 / step_budget | (0.563, 0.148, 0.291)→(0.563, 0.148, 0.319) | (0.462, 0.043, 0.016)→(0.462, 0.043, 0.016) | 0.293→0.293 |
| retract_from_goal | retract | 1.00 / step_budget | (0.563, 0.148, 0.319)→(0.603, 0.202, 0.380) | (0.462, 0.043, 0.016)→(0.462, 0.043, 0.016) | 0.293→0.293 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.230
- phase_score: 0.095
- phase_breakdown.reach_goal_score: 0.051
- phase_breakdown.grasp_lift_score: 0.178
- phase_breakdown.reach_object_score: 0.070
- grasp_place_fitness: 0.267

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.267
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.230
- **Median Q (composite search score)**: -0.526
- **K-run variance**: 0.0015
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.317


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":26.0,"average_failure_rate":0.10924,"average_mean_iterations":25.67227,"average_solve_count":238.0,"average_success_count":212.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_goal.approach_goal_speed":0.06647,"approach_to_object.approach_height":0.16791,"approach_to_object.approach_speed":0.1188,"descend_to_goal.descend_goal_speed":0.06856,"descend_to_goal.placement_z":0.0044,"descend_to_object.descend_speed":0.03099,"descend_to_object.grasp_offset_z":0.02002,"lift_object.lift_height":0.16369,"lift_object.lift_speed":0.03185,"retract_from_goal.retract_height":0.21124,"retract_from_goal.retract_speed":0.04716},"optimized_scores":{"best_composite_score":-0.46292,"best_fitness_score":0.26708,"best_task_score":0.22953},"replay_outcomes":[{"contacts":{"omitted_contact_groups":11,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":911.0,"contact_point_centroid":[0.63819,0.08617,-0.0004],"force_p95":427.91586,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1364.81269,"mean_force":321.9361,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.60643,0.11724,0.28948]},{"body_a":"world","body_b":"hand","contact_count":245.0,"contact_point_centroid":[0.58304,0.12836,-0.00112],"force_p95":465.87668,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1160.04389,"mean_force":180.88843,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.49603,0.08931,0.03381]},{"body_a":"world","body_b":"link6","contact_count":741.0,"contact_point_centroid":[0.68616,0.01164,-0.00024],"force_p95":275.58412,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":693.28648,"mean_force":221.01816,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.46676,0.11523,0.07095]},{"body_a":"world","body_b":"link7","contact_count":31.0,"contact_point_centroid":[0.59682,0.03835,-0.00049],"force_p95":587.36356,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":641.11805,"mean_force":192.17616,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.46183,0.07875,0.03947]},{"body_a":"world","body_b":"link6","contact_count":497.0,"contact_point_centroid":[0.69597,0.01462,-0.00013],"force_p95":78.50008,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":240.48819,"mean_force":69.94102,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47135,0.12503,0.08712]},{"body_a":"world","body_b":"link6","contact_count":85.0,"contact_point_centroid":[0.65564,0.11976,-0.00013],"force_p95":75.55035,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":117.88457,"mean_force":56.09435,"phase_index":6.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.62084,0.14252,0.29128]},{"body_a":"world","body_b":"link6","contact_count":7.0,"contact_point_centroid":[0.6961,0.01479,-9e-05],"force_p95":85.23927,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":85.4186,"mean_force":75.44567,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47146,0.12526,0.08707]},{"body_a":"world","body_b":"hand","contact_count":471.0,"contact_point_centroid":[0.57487,0.1412,-1e-05],"force_p95":20.80173,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":75.75018,"mean_force":6.32787,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47136,0.12504,0.08711]},{"body_a":"world","body_b":"right_finger","contact_count":1415.0,"contact_point_centroid":[0.54126,0.08527,-0.00773],"force_p95":11.18609,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":45.54132,"mean_force":5.973,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.52713,0.04734,-0.0039]},{"body_a":"world","body_b":"left_finger","contact_count":894.0,"contact_point_centroid":[0.52041,0.0027,-0.00934],"force_p95":9.36017,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":36.80221,"mean_force":5.32825,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.53086,0.04359,-0.00966]},{"body_a":"world","body_b":"hand","contact_count":4.0,"contact_point_centroid":[0.57505,0.14142,-1e-05],"force_p95":20.39735,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":22.1307,"mean_force":8.62159,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47147,0.12526,0.08702]},{"body_a":"world","body_b":"grasp_target","contact_count":3419.0,"contact_point_centroid":[0.47453,0.08769,-0.00212],"force_p95":0.3569,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.84299,"mean_force":0.16292,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.48461,0.10068,0.06881]},{"body_a":"grasp_target","body_b":"hand","contact_count":94.0,"contact_point_centroid":[0.50058,0.06582,0.03271],"force_p95":0.95124,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.6801,"mean_force":0.39686,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.46032,0.08031,0.04427]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":258.0,"contact_point_centroid":[0.47711,0.11697,0.042],"force_p95":0.38003,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.80344,"mean_force":0.16914,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.45956,0.08368,0.04682]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":603.0,"contact_point_centroid":[0.50199,0.02702,0.01451],"force_p95":0.36919,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.66474,"mean_force":0.14758,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.51258,0.0603,0.01067]},{"body_a":"world","body_b":"grasp_target","contact_count":704.0,"contact_point_centroid":[0.51251,0.03972,-0.00182],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12332,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.50304,0.01455,0.25873]}],"total_contact_groups":27},"final_pose_error":0.01976,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.46134,0.10574,0.01602],"final_tcp_position":[0.62593,0.16465,0.33822],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"phases":[{"n_steps":177.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.50718,0.03079,0.21482],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18908,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46134,0.10574,0.01602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.22076,"object_to_goal_dist_start":0.21222,"object_z_max":0.03612,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.47133,0.12604,0.08745],"tcp_start":[0.50718,0.03079,0.21482],"tcp_to_object_dist_end":0.07492,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":100.0,"n_steps_budget":50.0,"object_pos_end":[0.46134,0.10574,0.01602],"object_pos_start":[0.46134,0.10574,0.01602],"object_to_goal_dist_end":0.22076,"object_to_goal_dist_start":0.22076,"object_z_max":0.01602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.47147,0.12525,0.08702],"tcp_start":[0.47147,0.12523,0.08702],"tcp_to_object_dist_end":0.07433,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":319.0,"n_steps_budget":1000.0,"object_pos_end":[0.46134,0.10574,0.01602],"object_pos_start":[0.46134,0.10574,0.01602],"object_to_goal_dist_end":0.22076,"object_to_goal_dist_start":0.22076,"object_z_max":0.01602,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"grasp_lift","tcp_end":[0.45957,0.10718,0.17003],"tcp_start":[0.46055,0.10843,0.16016],"tcp_to_object_dist_end":0.15403,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":451.0,"n_steps_budget":1000.0,"object_pos_end":[0.46134,0.10574,0.01602],"object_pos_start":[0.46134,0.10574,0.01602],"object_to_goal_dist_end":0.22076,"object_to_goal_dist_start":0.22076,"object_z_max":0.01602,"phase_name":"approach_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.55817,0.13778,0.21917],"tcp_start":[0.45957,0.10718,0.17003],"tcp_to_object_dist_end":0.22732,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46134,0.10574,0.01602],"object_pos_start":[0.46134,0.10574,0.01602],"object_to_goal_dist_end":0.22076,"object_to_goal_dist_start":0.22076,"object_z_max":0.01602,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.62081,0.14286,0.29092],"tcp_start":[0.55817,0.13778,0.21917],"tcp_to_object_dist_end":0.31997,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46134,0.10574,0.01602],"object_pos_start":[0.46134,0.10574,0.01602],"object_to_goal_dist_end":0.22076,"object_to_goal_dist_start":0.22076,"object_z_max":0.01602,"phase_name":"release_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.62099,0.14259,0.31718],"tcp_start":[0.62081,0.14286,0.29092],"tcp_to_object_dist_end":0.34284,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":121.0,"n_steps_budget":690.0,"object_pos_end":[0.46134,0.10574,0.01602],"object_pos_start":[0.46134,0.10574,0.01602],"object_to_goal_dist_end":0.22076,"object_to_goal_dist_start":0.22076,"object_z_max":0.01602,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.62593,0.16465,0.33822],"tcp_start":[0.62099,0.14259,0.31718],"tcp_to_object_dist_end":0.36656,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":30.0,"average_failure_rate":0.08746,"average_mean_iterations":21.1137,"average_solve_count":343.0,"average_success_count":313.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_goal.approach_goal_speed":0.04121,"approach_to_object.approach_height":0.19894,"approach_to_object.approach_speed":0.02629,"descend_to_goal.descend_goal_speed":0.03145,"descend_to_goal.placement_z":0.01099,"descend_to_object.descend_speed":0.02724,"descend_to_object.grasp_offset_z":0.03716,"lift_object.lift_height":0.14119,"lift_object.lift_speed":0.0405,"retract_from_goal.retract_height":0.20389,"retract_from_goal.retract_speed":0.07612},"optimized_scores":{"best_composite_score":-0.52565,"best_fitness_score":0.20435,"best_task_score":0.12386},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":27.0,"contact_point_centroid":[0.49795,0.13315,-0.00317],"force_p95":826.38533,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":937.19121,"mean_force":147.14156,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.44064,0.0515,-0.00183]},{"body_a":"world","body_b":"link7","contact_count":65.0,"contact_point_centroid":[0.55661,0.03852,-0.00113],"force_p95":566.91305,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":856.26632,"mean_force":278.18582,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.42873,0.05454,0.02071]},{"body_a":"world","body_b":"link6","contact_count":892.0,"contact_point_centroid":[0.54801,0.18298,-0.00029],"force_p95":364.09877,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":397.86976,"mean_force":298.63924,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.55902,0.19509,0.29335]},{"body_a":"world","body_b":"link6","contact_count":835.0,"contact_point_centroid":[0.65243,0.02466,-0.00028],"force_p95":198.11043,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":340.05214,"mean_force":195.42728,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.41446,0.07431,0.07122]},{"body_a":"world","body_b":"link6","contact_count":501.0,"contact_point_centroid":[0.66051,0.02371,-0.00013],"force_p95":78.0535,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":159.52672,"mean_force":70.56346,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.42093,0.09474,0.08826]},{"body_a":"world","body_b":"link6","contact_count":83.0,"contact_point_centroid":[0.5544,0.19365,-0.00018],"force_p95":99.04008,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":99.6003,"mean_force":66.71822,"phase_index":6.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.56429,0.20342,0.29379]},{"body_a":"world","body_b":"link6","contact_count":9.0,"contact_point_centroid":[0.66061,0.02368,-0.0001],"force_p95":82.21126,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":92.89234,"mean_force":48.19195,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.42099,0.09468,0.08823]},{"body_a":"world","body_b":"right_finger","contact_count":475.0,"contact_point_centroid":[0.45083,0.09289,-0.00419],"force_p95":26.8474,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":40.11696,"mean_force":2.89553,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.44168,0.0515,-0.00208]},{"body_a":"world","body_b":"left_finger","contact_count":390.0,"contact_point_centroid":[0.43791,0.00896,-0.00373],"force_p95":10.84214,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":33.43038,"mean_force":2.62703,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.44149,0.0515,-0.00302]},{"body_a":"grasp_target","body_b":"hand","contact_count":266.0,"contact_point_centroid":[0.47008,0.05809,0.03091],"force_p95":1.02802,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.02747,"mean_force":0.4109,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.41929,0.05889,0.04372]},{"body_a":"world","body_b":"grasp_target","contact_count":3901.0,"contact_point_centroid":[0.44215,0.05275,-0.00227],"force_p95":0.30225,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.514,"mean_force":0.14633,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.42444,0.07047,0.07652]},{"body_a":"world","body_b":"grasp_target","contact_count":596.0,"contact_point_centroid":[0.4827,0.04873,-0.00179],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12345,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.49266,0.01577,0.27363]},{"body_a":"world","body_b":"grasp_target","contact_count":2004.0,"contact_point_centroid":[0.43565,0.05343,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.42093,0.09474,0.08826]},{"body_a":"world","body_b":"grasp_target","contact_count":1036.0,"contact_point_centroid":[0.43565,0.05343,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.42555,0.0746,0.11755]},{"body_a":"world","body_b":"grasp_target","contact_count":3068.0,"contact_point_centroid":[0.43565,0.05343,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_to_goal","phase_type":"approach","tcp_position_centroid":[0.48278,0.11826,0.22374]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.43565,0.05343,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.5577,0.19398,0.29434]}],"total_contact_groups":23},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.43565,0.05343,0.01602],"final_tcp_position":[0.58119,0.22561,0.41472],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"phases":[{"n_steps":150.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.48497,0.03521,0.24337],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21778,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43565,0.05343,0.01602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.31328,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.42049,0.0951,0.08876],"tcp_start":[0.48497,0.03521,0.24337],"tcp_to_object_dist_end":0.08519,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":100.0,"n_steps_budget":50.0,"object_pos_end":[0.43565,0.05343,0.01602],"object_pos_start":[0.43565,0.05343,0.01602],"object_to_goal_dist_end":0.31328,"object_to_goal_dist_start":0.31328,"object_z_max":0.01602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.421,0.09476,0.08814],"tcp_start":[0.421,0.09476,0.08814],"tcp_to_object_dist_end":0.0844,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":259.0,"n_steps_budget":1000.0,"object_pos_end":[0.43565,0.05343,0.01602],"object_pos_start":[0.43565,0.05343,0.01602],"object_to_goal_dist_end":0.31328,"object_to_goal_dist_start":0.31328,"object_z_max":0.01602,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"grasp_lift","tcp_end":[0.43087,0.05742,0.14836],"tcp_start":[0.43014,0.06069,0.13953],"tcp_to_object_dist_end":0.13249,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":767.0,"n_steps_budget":1000.0,"object_pos_end":[0.43565,0.05343,0.01602],"object_pos_start":[0.43565,0.05343,0.01602],"object_to_goal_dist_end":0.31328,"object_to_goal_dist_start":0.31328,"object_z_max":0.01602,"phase_name":"approach_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.53577,0.18282,0.30432],"tcp_start":[0.43087,0.05742,0.14836],"tcp_to_object_dist_end":0.33148,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43565,0.05343,0.01602],"object_pos_start":[0.43565,0.05343,0.01602],"object_to_goal_dist_end":0.31328,"object_to_goal_dist_start":0.31328,"object_z_max":0.01602,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.56421,0.20372,0.29345],"tcp_start":[0.53577,0.18282,0.30432],"tcp_to_object_dist_end":0.34071,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.43565,0.05343,0.01602],"object_pos_start":[0.43565,0.05343,0.01602],"object_to_goal_dist_end":0.31328,"object_to_goal_dist_start":0.31328,"object_z_max":0.01602,"phase_name":"release_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.56459,0.20303,0.32083],"tcp_start":[0.56421,0.20372,0.29345],"tcp_to_object_dist_end":0.36319,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":350.0,"n_steps_budget":960.0,"object_pos_end":[0.43565,0.05343,0.01602],"object_pos_start":[0.43565,0.05343,0.01602],"object_to_goal_dist_end":0.31328,"object_to_goal_dist_start":0.31328,"object_z_max":0.01602,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.58119,0.22561,0.41472],"tcp_start":[0.56459,0.20303,0.32083],"tcp_to_object_dist_end":0.45802,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":88.0,"average_failure_rate":0.32959,"average_mean_iterations":69.30712,"average_solve_count":267.0,"average_success_count":179.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_goal.approach_goal_speed":0.06617,"approach_to_object.approach_height":0.18715,"approach_to_object.approach_speed":0.07996,"descend_to_goal.descend_goal_speed":0.06533,"descend_to_goal.placement_z":0.00949,"descend_to_object.descend_speed":0.05834,"descend_to_object.grasp_offset_z":0.04202,"lift_object.lift_height":0.17405,"lift_object.lift_speed":0.07985,"retract_from_goal.retract_height":0.19534,"retract_from_goal.retract_speed":0.07931},"optimized_scores":{"best_composite_score":-0.55549,"best_fitness_score":0.17451,"best_task_score":0.10038},"replay_outcomes":[{"contacts":{"omitted_contact_groups":13,"reported_contact_groups":[{"body_a":"world","body_b":"link5","contact_count":416.0,"contact_point_centroid":[0.44931,0.11144,-0.00032],"force_p95":461.04107,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1314.74807,"mean_force":214.41741,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.49367,0.07105,0.27553]},{"body_a":"world","body_b":"hand","contact_count":140.0,"contact_point_centroid":[0.58307,-0.09849,-0.00195],"force_p95":672.53915,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1087.22754,"mean_force":256.31099,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.52764,-0.0274,-0.00313]},{"body_a":"link5","body_b":"hand","contact_count":357.0,"contact_point_centroid":[0.51744,-0.01198,0.17474],"force_p95":493.05234,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1016.0398,"mean_force":306.12454,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.47332,-0.09394,0.1128]},{"body_a":"world","body_b":"link7","contact_count":634.0,"contact_point_centroid":[0.59158,-0.09245,-0.00025],"force_p95":360.86003,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":779.06955,"mean_force":213.36263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.47089,-0.08263,0.09451]},{"body_a":"world","body_b":"link6","contact_count":300.0,"contact_point_centroid":[0.69397,-0.00228,-0.00017],"force_p95":272.51479,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":566.40416,"mean_force":162.97819,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.46625,-0.07217,0.07823]},{"body_a":"link5","body_b":"hand","contact_count":501.0,"contact_point_centroid":[0.52434,-0.00407,0.16929],"force_p95":156.48988,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":494.1087,"mean_force":101.02356,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47415,-0.08208,0.10681]},{"body_a":"world","body_b":"link7","contact_count":501.0,"contact_point_centroid":[0.59106,-0.10071,-0.00018],"force_p95":101.79233,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":410.42084,"mean_force":86.88181,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47415,-0.08208,0.10681]},{"body_a":"world","body_b":"link6","contact_count":837.0,"contact_point_centroid":[0.55405,0.10089,-0.0003],"force_p95":307.96092,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":316.95304,"mean_force":252.18597,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.50882,0.07008,0.28701]},{"body_a":"link5","body_b":"hand","contact_count":399.0,"contact_point_centroid":[0.53921,0.06606,0.22838],"force_p95":122.72359,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":214.1082,"mean_force":85.77118,"phase_index":4.0,"phase_name":"approach_to_goal","phase_type":"approach","tcp_position_centroid":[0.50302,-0.01711,0.16346]},{"body_a":"link5","body_b":"hand","contact_count":472.0,"contact_point_centroid":[0.5366,0.02638,0.20497],"force_p95":99.32485,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":163.11842,"mean_force":72.3319,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48111,-0.05271,0.14201]},{"body_a":"world","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.59111,-0.10094,-0.00014],"force_p95":89.28921,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":91.79533,"mean_force":66.69479,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47414,-0.08217,0.1068]},{"body_a":"world","body_b":"link5","contact_count":76.0,"contact_point_centroid":[0.43214,0.10394,-0.00011],"force_p95":61.64854,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":66.86363,"mean_force":46.45296,"phase_index":6.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.50432,0.09685,0.28913]},{"body_a":"world","body_b":"link6","contact_count":74.0,"contact_point_centroid":[0.55545,0.10541,-0.00012],"force_p95":48.2973,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":49.03955,"mean_force":32.56471,"phase_index":6.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.50432,0.09684,0.28913]},{"body_a":"world","body_b":"left_finger","contact_count":1857.0,"contact_point_centroid":[0.5384,-0.06679,-0.0067],"force_p95":11.51752,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":45.55833,"mean_force":5.02008,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.52938,-0.02671,-0.00303]},{"body_a":"world","body_b":"right_finger","contact_count":1254.0,"contact_point_centroid":[0.5292,0.01726,-0.00787],"force_p95":8.98091,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":39.19732,"mean_force":4.5113,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.5329,-0.02477,-0.00713]},{"body_a":"grasp_target","body_b":"hand","contact_count":274.0,"contact_point_centroid":[0.53273,-0.02454,0.03138],"force_p95":0.97733,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.77651,"mean_force":0.36008,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.48817,-0.04272,0.03119]}],"total_contact_groups":29},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.48779,-0.03159,0.01602],"final_tcp_position":[0.60266,0.21662,0.38809],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"phases":[{"n_steps":156.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.52529,-0.01598,0.23195],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20634,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48779,-0.03159,0.01602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.34482,"object_to_goal_dist_start":0.31672,"object_z_max":0.02629,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.47388,-0.08136,0.10739],"tcp_start":[0.52529,-0.01598,0.23195],"tcp_to_object_dist_end":0.10497,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":100.0,"n_steps_budget":50.0,"object_pos_end":[0.48779,-0.03159,0.01602],"object_pos_start":[0.48779,-0.03159,0.01602],"object_to_goal_dist_end":0.34482,"object_to_goal_dist_start":0.34482,"object_z_max":0.01602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.47415,-0.08221,0.10675],"tcp_start":[0.47415,-0.08219,0.10675],"tcp_to_object_dist_end":0.10479,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":522.0,"n_steps_budget":780.0,"object_pos_end":[0.48779,-0.03159,0.01602],"object_pos_start":[0.48779,-0.03159,0.01602],"object_to_goal_dist_end":0.34482,"object_to_goal_dist_start":0.34482,"object_z_max":0.01602,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"grasp_lift","tcp_end":[0.48625,-0.03182,0.18026],"tcp_start":[0.48719,-0.03307,0.16676],"tcp_to_object_dist_end":0.16425,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":519.0,"n_steps_budget":1000.0,"object_pos_end":[0.48779,-0.03159,0.01602],"object_pos_start":[0.48779,-0.03159,0.01602],"object_to_goal_dist_end":0.34482,"object_to_goal_dist_start":0.34482,"object_z_max":0.01602,"phase_name":"approach_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.49985,-0.0044,0.18962],"tcp_start":[0.48625,-0.03182,0.18026],"tcp_to_object_dist_end":0.17613,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48779,-0.03159,0.01602],"object_pos_start":[0.48779,-0.03159,0.01602],"object_to_goal_dist_end":0.34482,"object_to_goal_dist_start":0.34482,"object_z_max":0.01602,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_goal","tcp_end":[0.50428,0.09656,0.28886],"tcp_start":[0.49985,-0.0044,0.18962],"tcp_to_object_dist_end":0.30189,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48779,-0.03159,0.01602],"object_pos_start":[0.48779,-0.03159,0.01602],"object_to_goal_dist_end":0.34482,"object_to_goal_dist_start":0.34482,"object_z_max":0.01602,"phase_name":"release_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.5044,0.09736,0.3179],"tcp_start":[0.50428,0.09656,0.28886],"tcp_to_object_dist_end":0.32869,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":486.0,"n_steps_budget":1000.0,"object_pos_end":[0.48779,-0.03159,0.01602],"object_pos_start":[0.48779,-0.03159,0.01602],"object_to_goal_dist_end":0.34482,"object_to_goal_dist_start":0.34482,"object_z_max":0.01602,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.60266,0.21662,0.38809],"tcp_start":[0.5044,0.09736,0.3179],"tcp_to_object_dist_end":0.46178,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```