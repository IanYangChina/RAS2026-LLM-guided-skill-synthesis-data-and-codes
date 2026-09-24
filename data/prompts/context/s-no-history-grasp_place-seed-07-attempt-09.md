## Search State

- **Seed**: 7
- **Iteration**: 10 / 15

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 1.000, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.307) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: grasp_contact
  anchor: object
  weight: 0.2
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: place_goal
  weight: 0.4
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.1
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: grasp_contact
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.15
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift_object
- id: transport_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.05
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
    transport_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - -0.01
  parameters:
    descend_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    descend_x_offset:
      type: scalar
      range:
      - 0.0
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    descend_y_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: replace
    descend_z_offset:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: add
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1]
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15]
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.05]
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
    - transport_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, -0.01]
  - parameter_bindings:
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - descend_x_offset: status=consumed; consumers=target.offset.x (replace)
    - descend_y_offset: status=consumed; consumers=target.offset.y (replace)
    - descend_z_offset: status=consumed; consumers=target.offset.z (add)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.307
- **task_score** (E): 1.000
- **fitness_score**: 0.977  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.670

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1681 |
| descend_1 | 1.00 | 1.00 | 0.1037 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 0.33 | 1.00 | 0.1142 |
| transport_1 | 0.67 | 1.00 | 0.1979 |
| descend_2 | 1.00 | 1.00 | 0.0309 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.020, 0.138) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.020, 0.138)→(0.505, 0.022, 0.034) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.505, 0.022, 0.034)→(0.496, 0.021, 0.025) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.274 | 1.00 / 42.667 | 0.153 | 0.208 |
| lift_1 | lift | 0.33 / step_budget | (0.496, 0.021, 0.025)→(0.502, 0.021, 0.139) | (0.511, 0.022, 0.026)→(0.513, 0.022, 0.131) | 0.274→0.223 | 1.00 / 37.000 | 0.082 | 0.666 |
| transport_1 | approach | 0.67 / step_budget | (0.502, 0.021, 0.139)→(0.586, 0.178, 0.219) | (0.513, 0.022, 0.131)→(0.599, 0.182, 0.211) | 0.223→0.035 | 1.00 / 32.667 | 0.093 | 0.144 |
| descend_2 | descend | 1.00 / step_budget | (0.586, 0.178, 0.219)→(0.600, 0.193, 0.198) | (0.599, 0.182, 0.211)→(0.615, 0.198, 0.189) | 0.035→0.018 | 1.00 / 29.000 | 0.104 | 0.320 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.101
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.805
- phase_breakdown.lift_object_score: 0.822
- phase_breakdown.place_goal_score: 0.756
- phase_breakdown.reach_object_score: 0.819
- phase_breakdown.grasp_contact_score: 0.874
- grasp_place_fitness: 0.978

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.978
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.307
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.284


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05439,"average_solve_count":239.0,"average_success_count":239.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06817,"descend_1.speed":0.02635,"descend_2.descend_tolerance":0.02715,"descend_2.descend_x_offset":0.00969,"descend_2.descend_y_offset":-0.00527,"descend_2.descend_z_offset":0.02192,"descend_2.speed":0.03406,"lift_1.lift_height":0.16767,"lift_1.lift_speed":0.05965,"transport_1.speed":0.14147,"transport_1.transport_tolerance":0.0565},"optimized_scores":{"best_composite_score":0.30737,"best_fitness_score":0.97737,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":208.0,"contact_point_centroid":[0.50779,0.037,-0.00121],"force_p95":0.44579,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63852,"mean_force":0.10639,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49656,0.03804,0.02658]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.49856,0.05718,0.07524],"force_p95":0.08326,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2851,"mean_force":0.05871,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49822,0.03798,0.07248]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1051.0,"contact_point_centroid":[0.59958,0.16266,0.16723],"force_p95":0.09447,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26836,"mean_force":0.06615,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60266,0.14387,0.16374]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20735.0,"contact_point_centroid":[0.50003,0.01905,0.07308],"force_p95":0.07871,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25664,"mean_force":0.0496,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49813,0.03798,0.07151]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51258,0.03959,-0.00213],"force_p95":0.16221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2309,"mean_force":0.13291,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49951,0.0383,0.02613]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1267.0,"contact_point_centroid":[0.60694,0.12522,0.16427],"force_p95":0.07963,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1835,"mean_force":0.0525,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60258,0.14381,0.16379]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2912.0,"contact_point_centroid":[0.54998,0.06659,0.14389],"force_p95":0.10185,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18177,"mean_force":0.05548,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54685,0.08535,0.14288]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5233.0,"contact_point_centroid":[0.49967,0.01919,0.02651],"force_p95":0.06807,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.179,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49825,0.0382,0.02479]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2384.0,"contact_point_centroid":[0.54543,0.10421,0.1459],"force_p95":0.1012,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15121,"mean_force":0.06377,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54673,0.08522,0.14282]},{"body_a":"world","body_b":"grasp_target","contact_count":2188.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50257,0.01774,0.21874]},{"body_a":"world","body_b":"grasp_target","contact_count":1468.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50569,0.03745,0.08572]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4242.0,"contact_point_centroid":[0.4987,0.05755,0.0276],"force_p95":0.08274,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09549,"mean_force":0.05198,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49826,0.0382,0.02479]}],"total_contact_groups":12},"final_pose_error":0.02701,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62706,0.15575,0.14925],"final_tcp_position":[0.61461,0.15252,0.15708],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.63852,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":548.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2188.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50751,0.03628,0.1378],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11194,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":367.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1468.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.50695,0.0389,0.03419],"tcp_start":[0.50751,0.03628,0.1378],"tcp_to_object_dist_end":0.00992,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.03866,0.02554],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.2132,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15957,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11275.0,"raw_peak_contact_force":0.2309,"tcp_end":[0.49823,0.0382,0.02476],"tcp_start":[0.50695,0.0389,0.03419],"tcp_to_object_dist_end":0.01423,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51388,0.03898,0.11326],"object_pos_start":[0.51243,0.03866,0.02554],"object_to_goal_dist_end":0.17823,"object_to_goal_dist_start":0.2132,"object_z_max":0.11316,"peak_contact_force":0.08102,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37943.0,"raw_peak_contact_force":0.63852,"subtask_id":"lift_object","tcp_end":[0.50254,0.03813,0.12157],"tcp_start":[0.49823,0.0382,0.02476],"tcp_to_object_dist_end":0.01408,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":141.0,"n_steps_budget":1000.0,"object_pos_end":[0.60296,0.13859,0.15999],"object_pos_start":[0.51388,0.03898,0.11326],"object_to_goal_dist_end":0.04451,"object_to_goal_dist_start":0.17823,"object_z_max":0.15963,"peak_contact_force":0.07919,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5296.0,"raw_peak_contact_force":0.18177,"tcp_end":[0.59415,0.13654,0.1681],"tcp_start":[0.50254,0.03813,0.12157],"tcp_to_object_dist_end":0.01215,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":63.0,"n_steps_budget":1000.0,"object_pos_end":[0.62706,0.15575,0.14925],"object_pos_start":[0.60296,0.13859,0.15999],"object_to_goal_dist_end":0.0173,"object_to_goal_dist_start":0.04451,"object_z_max":0.16069,"peak_contact_force":0.08958,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2318.0,"raw_peak_contact_force":0.26836,"subtask_id":"place_goal","tcp_end":[0.61461,0.15252,0.15708],"tcp_start":[0.59415,0.13654,0.1681],"tcp_to_object_dist_end":0.01506,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.85627,"average_solve_count":327.0,"average_success_count":327.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07376,"descend_1.speed":0.01987,"descend_2.descend_tolerance":0.01946,"descend_2.descend_x_offset":0.01023,"descend_2.descend_y_offset":-0.00206,"descend_2.descend_z_offset":0.00204,"descend_2.speed":0.01629,"lift_1.lift_height":0.19371,"lift_1.lift_speed":0.09067,"transport_1.speed":0.08085,"transport_1.transport_tolerance":0.04285},"optimized_scores":{"best_composite_score":0.30839,"best_fitness_score":0.97839,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":155.0,"contact_point_centroid":[0.47959,0.04585,-0.00125],"force_p95":0.48288,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71835,"mean_force":0.10221,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46778,0.04677,0.02776]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1055.0,"contact_point_centroid":[0.56712,0.22501,0.24939],"force_p95":0.11997,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.378,"mean_force":0.08954,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.56916,0.20606,0.24563]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.47043,0.06594,0.10104],"force_p95":0.08427,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3262,"mean_force":0.05877,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47047,0.04674,0.09833]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20808.0,"contact_point_centroid":[0.47257,0.02784,0.0988],"force_p95":0.07946,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29987,"mean_force":0.04945,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47039,0.04674,0.0973]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1412.0,"contact_point_centroid":[0.57867,0.18988,0.24487],"force_p95":0.10217,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24468,"mean_force":0.06893,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.56958,0.20648,0.24482]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4828,0.04857,-0.00216],"force_p95":0.16905,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23991,"mean_force":0.13495,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47039,0.04705,0.02702]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4984.0,"contact_point_centroid":[0.47118,0.02796,0.02708],"force_p95":0.07892,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19626,"mean_force":0.0432,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46918,0.04693,0.02581]},{"body_a":"world","body_b":"grasp_target","contact_count":2096.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48925,0.02164,0.21944]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4832.0,"contact_point_centroid":[0.52176,0.09979,0.21067],"force_p95":0.09057,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12759,"mean_force":0.05795,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51644,0.1179,0.21015]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4052.0,"contact_point_centroid":[0.51465,0.13638,0.21227],"force_p95":0.09901,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12737,"mean_force":0.06615,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51612,0.11735,0.20984]},{"body_a":"world","body_b":"grasp_target","contact_count":1560.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47738,0.0459,0.08639]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4252.0,"contact_point_centroid":[0.46919,0.06628,0.02831],"force_p95":0.08586,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.101,"mean_force":0.05208,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46919,0.04694,0.02581]}],"total_contact_groups":12},"final_pose_error":0.01924,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.59537,0.22158,0.22111],"final_tcp_position":[0.57854,0.21527,0.22981],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.71835,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":525.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2096.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4802,0.0444,0.13866],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11275,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":390.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1560.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.47758,0.04775,0.0343],"tcp_start":[0.4802,0.0444,0.13866],"tcp_to_object_dist_end":0.00979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4827,0.04746,0.02545],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29117,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16533,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11036.0,"raw_peak_contact_force":0.23991,"tcp_end":[0.46915,0.04693,0.02578],"tcp_start":[0.47758,0.04775,0.0343],"tcp_to_object_dist_end":0.01356,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48721,0.04799,0.16439],"object_pos_start":[0.4827,0.04746,0.02545],"object_to_goal_dist_end":0.21457,"object_to_goal_dist_start":0.29117,"object_z_max":0.16421,"peak_contact_force":0.08186,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37963.0,"raw_peak_contact_force":0.71835,"subtask_id":"lift_object","tcp_end":[0.47608,0.04698,0.17302],"tcp_start":[0.46915,0.04693,0.02578],"tcp_to_object_dist_end":0.01412,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":261.0,"n_steps_budget":1000.0,"object_pos_end":[0.57917,0.20483,0.24852],"object_pos_start":[0.48721,0.04799,0.16439],"object_to_goal_dist_end":0.03017,"object_to_goal_dist_start":0.21457,"object_z_max":0.24819,"peak_contact_force":0.10388,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8884.0,"raw_peak_contact_force":0.12759,"tcp_end":[0.5639,0.19956,0.25611],"tcp_start":[0.47608,0.04698,0.17302],"tcp_to_object_dist_end":0.01785,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":94.0,"n_steps_budget":1000.0,"object_pos_end":[0.59537,0.22158,0.22111],"object_pos_start":[0.57917,0.20483,0.24852],"object_to_goal_dist_end":0.01797,"object_to_goal_dist_start":0.03017,"object_z_max":0.24901,"peak_contact_force":0.11435,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2467.0,"raw_peak_contact_force":0.378,"subtask_id":"place_goal","tcp_end":[0.57854,0.21527,0.22981],"tcp_start":[0.5639,0.19956,0.25611],"tcp_to_object_dist_end":0.01997,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0,"average_solve_count":345.0,"average_success_count":345.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.02261,"descend_1.speed":0.02937,"descend_2.descend_tolerance":0.02112,"descend_2.descend_x_offset":0.00581,"descend_2.descend_y_offset":-0.00395,"descend_2.descend_z_offset":-0.00398,"descend_2.speed":0.02889,"lift_1.lift_height":0.15978,"lift_1.lift_speed":0.06049,"transport_1.speed":0.08314,"transport_1.transport_tolerance":0.03942},"optimized_scores":{"best_composite_score":0.30636,"best_fitness_score":0.97636,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":194.0,"contact_point_centroid":[0.53239,-0.02076,-0.00111],"force_p95":0.47386,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64063,"mean_force":0.10706,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52052,-0.02089,0.0255]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":985.0,"contact_point_centroid":[0.59995,0.22355,0.22646],"force_p95":0.10575,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31268,"mean_force":0.07367,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60146,0.20446,0.2234]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.5233,-0.04012,0.07476],"force_p95":0.08124,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27753,"mean_force":0.05887,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52244,-0.02093,0.07205]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20349.0,"contact_point_centroid":[0.52402,-0.00197,0.07296],"force_p95":0.07731,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27042,"mean_force":0.05088,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52239,-0.02093,0.07135]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":924.0,"contact_point_centroid":[0.61033,0.18731,0.22396],"force_p95":0.10818,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22481,"mean_force":0.07516,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60144,0.20442,0.22348]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53701,-0.02133,-0.00203],"force_p95":0.1342,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15301,"mean_force":0.12549,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52343,-0.02093,0.02535]},{"body_a":"world","body_b":"grasp_target","contact_count":2412.0,"contact_point_centroid":[0.53702,-0.02132,-0.00194],"force_p95":0.13067,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51361,-0.00962,0.21816]},{"body_a":"world","body_b":"grasp_target","contact_count":1416.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52903,-0.02029,0.08513]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6255.0,"contact_point_centroid":[0.56494,0.06611,0.17415],"force_p95":0.08931,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12205,"mean_force":0.06176,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56037,0.08446,0.17354]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5793.0,"contact_point_centroid":[0.55985,0.10292,0.17529],"force_p95":0.09256,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11269,"mean_force":0.06447,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56022,0.08397,0.1733]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5312.0,"contact_point_centroid":[0.5232,-0.00187,0.02619],"force_p95":0.06872,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09694,"mean_force":0.0409,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52214,-0.02091,0.0239]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4158.0,"contact_point_centroid":[0.52316,-0.04021,0.02659],"force_p95":0.08021,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.095,"mean_force":0.05201,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52215,-0.02091,0.0239]}],"total_contact_groups":12},"final_pose_error":0.02097,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.62281,0.21751,0.19755],"final_tcp_position":[0.60594,0.2116,0.20711],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.64063,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":604.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2412.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.5301,-0.01962,0.13693],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11114,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":354.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1416.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.53107,-0.02103,0.03404],"tcp_start":[0.5301,-0.01962,0.13693],"tcp_to_object_dist_end":0.01,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53687,-0.0212,0.02586],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31675,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13418,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11270.0,"raw_peak_contact_force":0.15301,"tcp_end":[0.52211,-0.02091,0.02386],"tcp_start":[0.53107,-0.02103,0.03404],"tcp_to_object_dist_end":0.0149,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53921,-0.02161,0.11392],"object_pos_start":[0.53687,-0.0212,0.02586],"object_to_goal_dist_end":0.27564,"object_to_goal_dist_start":0.31675,"object_z_max":0.11381,"peak_contact_force":0.08287,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37543.0,"raw_peak_contact_force":0.64063,"subtask_id":"lift_object","tcp_end":[0.52721,-0.02102,0.12188],"tcp_start":[0.52211,-0.02091,0.02386],"tcp_to_object_dist_end":0.01441,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":373.0,"n_steps_budget":1000.0,"object_pos_end":[0.61392,0.20389,0.22519],"object_pos_start":[0.53921,-0.02161,0.11392],"object_to_goal_dist_end":0.02997,"object_to_goal_dist_start":0.27564,"object_z_max":0.22488,"peak_contact_force":0.09627,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12048.0,"raw_peak_contact_force":0.12205,"tcp_end":[0.59885,0.19872,0.23384],"tcp_start":[0.52721,-0.02102,0.12188],"tcp_to_object_dist_end":0.01813,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":69.0,"n_steps_budget":1000.0,"object_pos_end":[0.62281,0.21751,0.19755],"object_pos_start":[0.61392,0.20389,0.22519],"object_to_goal_dist_end":0.01893,"object_to_goal_dist_start":0.02997,"object_z_max":0.22553,"peak_contact_force":0.10819,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1909.0,"raw_peak_contact_force":0.31268,"subtask_id":"place_goal","tcp_end":[0.60594,0.2116,0.20711],"tcp_start":[0.59885,0.19872,0.23384],"tcp_to_object_dist_end":0.02027,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```