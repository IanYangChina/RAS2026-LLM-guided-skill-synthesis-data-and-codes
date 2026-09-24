## Search State

- **Seed**: 7
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.3909 | 0.18 | ❌ rejected |
| 5 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | -0.0468 | 0.17 | ❌ rejected |
| 3 | descend → grasp → lift → approach → align → descend → release → retract | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | -0.3520 | 0.17 | ❌ rejected |
| 2 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ❌ rejected |

**Proposal policy**: task_score is 0.18 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.391) — your mutation base

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

- **Composite score**: -0.391
- **task_score** (E): 0.178
- **fitness_score**: 0.289  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.680

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1682 |
| descend_1 | 1.00 | 0.0735 |
| grasp_1 | 1.00 | 0.0118 |
| lift_1 | 1.00 | 0.0110 |
| approach_goal_1 | 0.00 | 0.0853 |
| descend_goal_1 | 0.67 | 0.1001 |
| release_1 | 1.00 | 0.0228 |
| retract_1 | 0.67 | 0.0632 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.020, 0.138) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.020, 0.138)→(0.506, 0.022, 0.064) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.022, 0.064)→(0.498, 0.021, 0.055) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.025) | 0.273→0.274 |
| lift_1 | lift | 1.00 / step_budget | (0.506, 0.022, 0.135)→(0.507, 0.031, 0.134) | (0.511, 0.022, 0.025)→(0.513, 0.036, 0.019) | 0.274→0.268 |
| approach_goal_1 | approach | 0.00 / step_budget | (0.507, 0.031, 0.134)→(0.540, 0.091, 0.182) | (0.512, 0.036, 0.019)→(0.512, 0.036, 0.019) | 0.268→0.268 |
| descend_goal_1 | descend | 0.67 / step_budget | (0.540, 0.091, 0.182)→(0.587, 0.171, 0.177) | (0.512, 0.036, 0.019)→(0.512, 0.036, 0.019) | 0.268→0.268 |
| release_1 | release | 1.00 / step_budget | (0.587, 0.171, 0.177)→(0.581, 0.170, 0.199) | (0.512, 0.036, 0.019)→(0.512, 0.036, 0.019) | 0.268→0.268 |
| retract_1 | retract | 0.67 / step_budget | (0.581, 0.170, 0.199)→(0.594, 0.193, 0.252) | (0.512, 0.036, 0.019)→(0.512, 0.036, 0.019) | 0.268→0.268 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.266
- phase_score: 0.616
- phase_breakdown.lift_object_score: 0.492
- phase_breakdown.approach_goal_score: 0.109
- phase_breakdown.place_goal_score: 0.819
- phase_breakdown.reach_object_score: 0.823
- grasp_place_fitness: 0.334

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.334
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.266
- **Median Q (composite search score)**: -0.410
- **K-run variance**: 0.0010
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: lift_1.lift_height
- **Final σ (mean)**: 0.344


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.128,"average_solve_count":250.0,"average_success_count":250.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05744,"approach_goal_1.speed":0.04007,"descend_1.speed":0.09225,"descend_goal_1.speed":0.05239,"grasp_1.grasp_offset_x":0.00384,"grasp_1.grasp_offset_y":-0.00992,"lift_1.lift_height":0.14396,"lift_1.speed":0.09598,"retract_1.retract_height":0.12886,"retract_1.speed":0.04541},"optimized_scores":{"best_composite_score":-0.34567,"best_fitness_score":0.33433,"best_task_score":0.26623},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1676.0,"contact_point_centroid":[0.51373,0.06719,-0.00243],"force_p95":0.30241,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.93625,"mean_force":0.14701,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50673,0.04431,0.13959]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3279.0,"contact_point_centroid":[0.49961,0.05592,0.07771],"force_p95":0.15192,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35713,"mean_force":0.11396,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49926,0.03806,0.08179]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3225.0,"contact_point_centroid":[0.49926,0.01997,0.07419],"force_p95":0.17075,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31498,"mean_force":0.10061,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49887,0.03804,0.07809]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.0397,-0.0021],"force_p95":0.1532,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19855,"mean_force":0.13019,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50055,0.03822,0.05672]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2701.0,"contact_point_centroid":[0.50038,0.01959,0.05181],"force_p95":0.11037,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16264,"mean_force":0.07477,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49944,0.03812,0.05546]},{"body_a":"world","body_b":"grasp_target","contact_count":2260.0,"contact_point_centroid":[0.51251,0.03972,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50255,0.01776,0.21864]},{"body_a":"world","body_b":"grasp_target","contact_count":872.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50543,0.0372,0.09899]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5168,0.07008,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"approach_goal_1","phase_type":"approach","tcp_position_centroid":[0.53527,0.08893,0.16972]},{"body_a":"world","body_b":"grasp_target","contact_count":3340.0,"contact_point_centroid":[0.5168,0.07008,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_goal_1","phase_type":"descend","tcp_position_centroid":[0.59143,0.14248,0.1574]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5168,0.07008,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61652,0.16787,0.13971]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5168,0.07008,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.61631,0.16838,0.19438]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2539.0,"contact_point_centroid":[0.49989,0.0569,0.05227],"force_p95":0.11633,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11676,"mean_force":0.08038,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49945,0.03812,0.05546]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1573.0,"contact_point_centroid":[0.50748,0.04527,0.15142],"force_p95":0.01156,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01655,"mean_force":0.01054,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50777,0.04529,0.14917]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4254.0,"contact_point_centroid":[0.53504,0.08892,0.17186],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.01048,"phase_index":4.0,"phase_name":"approach_goal_1","phase_type":"approach","tcp_position_centroid":[0.53531,0.08897,0.16976]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.61879,0.16848,0.13749],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01277,"mean_force":0.01011,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61933,0.1687,0.13567]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3590.0,"contact_point_centroid":[0.59083,0.14222,0.15959],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01038,"phase_index":5.0,"phase_name":"descend_goal_1","phase_type":"descend","tcp_position_centroid":[0.59136,0.14241,0.15745]}],"total_contact_groups":16},"final_pose_error":0.04302,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.5168,0.07008,0.01602],"final_tcp_position":[0.62067,0.17011,0.23149],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"phases":[{"n_steps":566.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.5075,0.03631,0.13766],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1118,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":218.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"contact_object","tcp_end":[0.50722,0.03875,0.06437],"tcp_start":[0.5075,0.03631,0.13766],"tcp_to_object_dist_end":0.03873,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51255,0.03903,0.02564],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21284,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.49941,0.03812,0.05542],"tcp_start":[0.50722,0.03875,0.06437],"tcp_to_object_dist_end":0.03257,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":846.0,"n_steps_budget":750.0,"object_pos_end":[0.51678,0.07008,0.01602],"object_pos_start":[0.51255,0.03903,0.02564],"object_to_goal_dist_end":0.19852,"object_to_goal_dist_start":0.21284,"object_z_max":0.06832,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.51152,0.06399,0.15416],"tcp_start":[0.50815,0.03869,0.15781],"tcp_to_object_dist_end":0.13837,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5168,0.07008,0.01602],"object_pos_start":[0.5168,0.07008,0.01602],"object_to_goal_dist_end":0.19851,"object_to_goal_dist_start":0.19851,"object_z_max":0.01602,"phase_name":"approach_goal_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_goal","tcp_end":[0.55753,0.10969,0.18645],"tcp_start":[0.51152,0.06399,0.15416],"tcp_to_object_dist_end":0.17965,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":835.0,"n_steps_budget":1000.0,"object_pos_end":[0.5168,0.07008,0.01602],"object_pos_start":[0.5168,0.07008,0.01602],"object_to_goal_dist_end":0.19851,"object_to_goal_dist_start":0.19851,"object_z_max":0.01602,"phase_name":"descend_goal_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.62081,0.16903,0.13856],"tcp_start":[0.55753,0.10969,0.18645],"tcp_to_object_dist_end":0.18874,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5168,0.07008,0.01602],"object_pos_start":[0.5168,0.07008,0.01602],"object_to_goal_dist_end":0.19851,"object_to_goal_dist_start":0.19851,"object_z_max":0.01602,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.61483,0.16737,0.15953],"tcp_start":[0.62081,0.16903,0.13856],"tcp_to_object_dist_end":0.19917,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5168,0.07008,0.01602],"object_pos_start":[0.5168,0.07008,0.01602],"object_to_goal_dist_end":0.19851,"object_to_goal_dist_start":0.19851,"object_z_max":0.01602,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.62067,0.17011,0.23149],"tcp_start":[0.61483,0.16737,0.15953],"tcp_to_object_dist_end":0.25928,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.56021,"average_solve_count":382.0,"average_success_count":382.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05636,"approach_goal_1.speed":0.0308,"descend_1.speed":0.01007,"descend_goal_1.speed":0.04084,"grasp_1.grasp_offset_x":0.00121,"grasp_1.grasp_offset_y":0.00271,"lift_1.lift_height":0.13604,"lift_1.speed":0.08792,"retract_1.retract_height":0.12264,"retract_1.speed":0.01008},"optimized_scores":{"best_composite_score":-0.41023,"best_fitness_score":0.26977,"best_task_score":0.14539},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2774.0,"contact_point_centroid":[0.48207,0.04913,-0.00208],"force_p95":0.17935,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38247,"mean_force":0.1271,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47371,0.04676,0.10923]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":363.0,"contact_point_centroid":[0.47428,0.03131,0.05272],"force_p95":0.20314,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29635,"mean_force":0.10612,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46966,0.0467,0.05889]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48279,0.04922,-0.00245],"force_p95":0.27317,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28845,"mean_force":0.15772,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47174,0.04696,0.05775]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":902.0,"contact_point_centroid":[0.46829,0.06076,0.05659],"force_p95":0.09843,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26011,"mean_force":0.0525,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4693,0.04665,0.06087]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2505.0,"contact_point_centroid":[0.4721,0.02854,0.05146],"force_p95":0.14189,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22005,"mean_force":0.08845,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47068,0.04685,0.05662]},{"body_a":"world","body_b":"grasp_target","contact_count":2208.0,"contact_point_centroid":[0.4827,0.04873,-0.00194],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48921,0.02164,0.2194]},{"body_a":"world","body_b":"grasp_target","contact_count":1028.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47679,0.04554,0.09957]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.48201,0.05029,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_goal_1","phase_type":"approach","tcp_position_centroid":[0.49392,0.08165,0.18108]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.48201,0.05029,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_goal_1","phase_type":"descend","tcp_position_centroid":[0.53553,0.15602,0.21155]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.48201,0.05029,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5556,0.19362,0.22011]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.48201,0.05029,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55843,0.20083,0.26089]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2792.0,"contact_point_centroid":[0.46916,0.06425,0.05274],"force_p95":0.10075,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1086,"mean_force":0.06451,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47069,0.04685,0.05663]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2271.0,"contact_point_centroid":[0.47475,0.04681,0.12258],"force_p95":0.0114,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01635,"mean_force":0.01072,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47489,0.04681,0.12033]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4217.0,"contact_point_centroid":[0.49372,0.08186,0.18347],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01292,"mean_force":0.01056,"phase_index":4.0,"phase_name":"approach_goal_1","phase_type":"approach","tcp_position_centroid":[0.49406,0.0819,0.18132]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4373.0,"contact_point_centroid":[0.53493,0.1559,0.21362],"force_p95":0.0109,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01268,"mean_force":0.01022,"phase_index":5.0,"phase_name":"descend_goal_1","phase_type":"descend","tcp_position_centroid":[0.53558,0.15609,0.21156]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.55713,0.19418,0.21706],"force_p95":0.01091,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01092,"mean_force":0.0099,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55768,0.1944,0.21524]}],"total_contact_groups":16},"final_pose_error":0.0774,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.48201,0.05029,0.02602],"final_tcp_position":[0.56352,0.20737,0.28107],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"phases":[{"n_steps":553.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.48018,0.04441,0.13864],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11273,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":257.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"contact_object","tcp_end":[0.47806,0.04758,0.06455],"tcp_start":[0.48018,0.04441,0.13864],"tcp_to_object_dist_end":0.03882,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48294,0.04717,0.02311],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29292,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.47066,0.04685,0.05661],"tcp_start":[0.47806,0.04758,0.06455],"tcp_to_object_dist_end":0.03568,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":737.0,"n_steps_budget":750.0,"object_pos_end":[0.48201,0.05029,0.02602],"object_pos_start":[0.48294,0.04717,0.02311],"object_to_goal_dist_end":0.28925,"object_to_goal_dist_start":0.29292,"object_z_max":0.02952,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.47787,0.04868,0.15314],"tcp_start":[0.47864,0.04681,0.14858],"tcp_to_object_dist_end":0.12719,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48201,0.05029,0.02602],"object_pos_start":[0.48201,0.05029,0.02602],"object_to_goal_dist_end":0.28925,"object_to_goal_dist_start":0.28925,"object_z_max":0.02602,"phase_name":"approach_goal_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_goal","tcp_end":[0.51081,0.11073,0.20919],"tcp_start":[0.47787,0.04868,0.15314],"tcp_to_object_dist_end":0.19503,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48201,0.05029,0.02602],"object_pos_start":[0.48201,0.05029,0.02602],"object_to_goal_dist_end":0.28925,"object_to_goal_dist_start":0.28925,"object_z_max":0.02602,"phase_name":"descend_goal_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.55881,0.19465,0.21765],"tcp_start":[0.51081,0.11073,0.20919],"tcp_to_object_dist_end":0.25192,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48201,0.05029,0.02602],"object_pos_start":[0.48201,0.05029,0.02602],"object_to_goal_dist_end":0.28925,"object_to_goal_dist_start":0.28925,"object_z_max":0.02602,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.55439,0.19317,0.24047],"tcp_start":[0.55881,0.19465,0.21765],"tcp_to_object_dist_end":0.26766,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48201,0.05029,0.02602],"object_pos_start":[0.48201,0.05029,0.02602],"object_to_goal_dist_end":0.28925,"object_to_goal_dist_start":0.28925,"object_z_max":0.02602,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.56352,0.20737,0.28107],"tcp_start":[0.55439,0.19317,0.24047],"tcp_to_object_dist_end":0.31043,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.8255,"average_solve_count":298.0,"average_success_count":298.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06497,"approach_goal_1.speed":0.07687,"descend_1.speed":0.07556,"descend_goal_1.speed":0.09999,"grasp_1.grasp_offset_x":-0.00869,"grasp_1.grasp_offset_y":0.00194,"lift_1.lift_height":0.08,"lift_1.speed":0.01001,"retract_1.retract_height":0.06717,"retract_1.speed":0.04427},"optimized_scores":{"best_composite_score":-0.41692,"best_fitness_score":0.26308,"best_task_score":0.1213},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":661.0,"contact_point_centroid":[0.53317,-0.02051,-0.00211],"force_p95":0.53469,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74361,"mean_force":0.1718,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5253,-0.02078,0.0707]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9512.0,"contact_point_centroid":[0.52584,-0.00226,0.06874],"force_p95":0.1219,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3252,"mean_force":0.08613,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5251,-0.0208,0.0724]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53704,-0.02132,-0.00204],"force_p95":0.19573,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19978,"mean_force":0.15405,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52436,-0.02076,0.05575]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9878.0,"contact_point_centroid":[0.52577,-0.03929,0.07001],"force_p95":0.10778,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19665,"mean_force":0.08238,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5254,-0.02081,0.07356]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2909.0,"contact_point_centroid":[0.52427,-0.0021,0.05123],"force_p95":0.11098,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14553,"mean_force":0.081,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5232,-0.02074,0.05437]},{"body_a":"world","body_b":"grasp_target","contact_count":2280.0,"contact_point_centroid":[0.53702,-0.02132,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51367,-0.00964,0.21806]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53794,-0.0136,-0.00199],"force_p95":0.12266,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13232,"mean_force":0.12245,"phase_index":4.0,"phase_name":"approach_goal_1","phase_type":"approach","tcp_position_centroid":[0.54005,0.01853,0.12262]},{"body_a":"world","body_b":"grasp_target","contact_count":876.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52905,-0.02013,0.09885]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53794,-0.0136,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_goal_1","phase_type":"descend","tcp_position_centroid":[0.56534,0.10511,0.16193]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53794,-0.0136,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57652,0.14848,0.1776]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53794,-0.0136,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58505,0.17663,0.21919]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2704.0,"contact_point_centroid":[0.52373,-0.03952,0.05159],"force_p95":0.11164,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11258,"mean_force":0.08613,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5232,-0.02074,0.05437]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4183.0,"contact_point_centroid":[0.54014,0.01945,0.12567],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0158,"mean_force":0.01048,"phase_index":4.0,"phase_name":"approach_goal_1","phase_type":"approach","tcp_position_centroid":[0.54029,0.01949,0.12334]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4271.0,"contact_point_centroid":[0.56502,0.10493,0.16423],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01044,"phase_index":5.0,"phase_name":"descend_goal_1","phase_type":"descend","tcp_position_centroid":[0.56532,0.10506,0.16191]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.57894,0.14906,0.17545],"force_p95":0.01088,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01267,"mean_force":0.0099,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57907,0.1492,0.17299]}],"total_contact_groups":15},"final_pose_error":0.0433,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.53794,-0.0136,0.01602],"final_tcp_position":[0.59634,0.20186,0.24282],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"phases":[{"n_steps":571.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.53008,-0.01962,0.13695],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11116,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":219.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"contact_object","tcp_end":[0.53129,-0.0209,0.06412],"tcp_start":[0.53008,-0.01962,0.13695],"tcp_to_object_dist_end":0.03854,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53696,-0.02111,0.02584],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31667,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.52317,-0.02074,0.05434],"tcp_start":[0.53129,-0.0209,0.06412],"tcp_to_object_dist_end":0.03166,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":981.0,"n_steps_budget":1000.0,"object_pos_end":[0.53926,-0.01362,0.01403],"object_pos_start":[0.53696,-0.02111,0.02584],"object_to_goal_dist_end":0.31734,"object_to_goal_dist_start":0.31667,"object_z_max":0.05404,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.53177,-0.02009,0.09524],"tcp_start":[0.53182,-0.02098,0.09729],"tcp_to_object_dist_end":0.08181,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53794,-0.0136,0.01602],"object_pos_start":[0.53842,-0.01291,0.01538],"object_to_goal_dist_end":0.31642,"object_to_goal_dist_start":0.31617,"object_z_max":0.0161,"phase_name":"approach_goal_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_goal","tcp_end":[0.55087,0.05233,0.15122],"tcp_start":[0.53177,-0.02009,0.09524],"tcp_to_object_dist_end":0.15097,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53794,-0.0136,0.01602],"object_pos_start":[0.53794,-0.0136,0.01602],"object_to_goal_dist_end":0.31642,"object_to_goal_dist_start":0.31642,"object_z_max":0.01602,"phase_name":"descend_goal_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_goal","tcp_end":[0.58038,0.14929,0.1754],"tcp_start":[0.55087,0.05233,0.15122],"tcp_to_object_dist_end":0.23181,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53794,-0.0136,0.01602],"object_pos_start":[0.53794,-0.0136,0.01602],"object_to_goal_dist_end":0.31642,"object_to_goal_dist_start":0.31642,"object_z_max":0.01602,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.57503,0.14806,0.19783],"tcp_start":[0.58038,0.14929,0.1754],"tcp_to_object_dist_end":0.2461,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53794,-0.0136,0.01602],"object_pos_start":[0.53794,-0.0136,0.01602],"object_to_goal_dist_end":0.31642,"object_to_goal_dist_start":0.31642,"object_z_max":0.01602,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.59634,0.20186,0.24282],"tcp_start":[0.57503,0.14806,0.19783],"tcp_to_object_dist_end":0.31823,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```