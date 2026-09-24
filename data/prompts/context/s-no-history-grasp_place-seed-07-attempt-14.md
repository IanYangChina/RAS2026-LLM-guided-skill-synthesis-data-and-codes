## Search State

- **Seed**: 7
- **Iteration**: 15 / 15

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

## Current Skill (Q=0.158) — your mutation base

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

- **Composite score**: 0.158
- **task_score** (E): 1.000
- **fitness_score**: 0.978  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.820

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1477 |
| descend_1 | 1.00 | 1.00 | 0.1228 |
| grasp_1 | 1.00 | 1.00 | 0.0129 |
| lift_1 | 1.00 | 1.00 | 0.1768 |
| transport_1 | 1.00 | 1.00 | 0.2082 |
| descend_2 | 1.00 | 1.00 | 0.0337 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, 0.017, 0.157) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.507, 0.017, 0.157)→(0.505, 0.022, 0.035) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.505, 0.022, 0.035)→(0.497, 0.021, 0.026) | (0.511, 0.022, 0.026)→(0.511, 0.021, 0.025) | 0.273→0.274 | 1.00 / 42.667 | 0.163 | 0.229 |
| lift_1 | lift | 1.00 / step_budget | (0.497, 0.021, 0.026)→(0.506, 0.021, 0.202) | (0.511, 0.021, 0.025)→(0.519, 0.022, 0.199) | 0.274→0.224 | 1.00 / 37.333 | 0.082 | 0.597 |
| transport_1 | approach | 1.00 / step_budget | (0.506, 0.021, 0.202)→(0.593, 0.192, 0.237) | (0.519, 0.022, 0.199)→(0.599, 0.194, 0.230) | 0.224→0.041 | 1.00 / 37.667 | 0.080 | 0.125 |
| descend_2 | descend | 1.00 / step_budget | (0.593, 0.192, 0.237)→(0.599, 0.202, 0.206) | (0.599, 0.194, 0.230)→(0.606, 0.204, 0.199) | 0.041→0.013 | 1.00 / 36.667 | 0.080 | 0.203 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.491
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.699
- phase_breakdown.lift_object_score: 0.545
- phase_breakdown.place_goal_score: 0.796
- phase_breakdown.reach_object_score: 0.488
- phase_breakdown.grasp_contact_score: 0.870
- grasp_place_fitness: 0.979

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.979
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.157
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at lower bound**: descend_2.descend_x_offset
- **Final σ (mean)**: 0.336


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.03743,"average_solve_count":374.0,"average_success_count":374.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_tolerance":0.02889,"approach_1.speed":0.02891,"descend_1.descend_tolerance":0.01016,"descend_1.speed":0.03,"descend_2.descend_tolerance":0.02782,"descend_2.descend_x_offset":0.00261,"descend_2.descend_y_offset":0.00601,"descend_2.descend_z_offset":0.00187,"descend_2.speed":0.03158,"lift_1.lift_height":0.24975,"lift_1.lift_speed":0.06865,"lift_1.lift_tolerance":0.01792,"transport_1.speed":0.0973,"transport_1.transport_tolerance":0.03607},"optimized_scores":{"best_composite_score":0.15743,"best_fitness_score":0.97743,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":91.0,"contact_point_centroid":[0.50844,0.03679,-0.00145],"force_p95":0.60291,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70997,"mean_force":0.16482,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49726,0.03771,0.02636]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15929.0,"contact_point_centroid":[0.50148,0.05695,0.14353],"force_p95":0.08332,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31535,"mean_force":0.05945,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50144,0.03775,0.14077]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19410.0,"contact_point_centroid":[0.50311,0.01882,0.14048],"force_p95":0.07932,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28677,"mean_force":0.05014,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50131,0.03775,0.13881]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51262,0.03954,-0.00218],"force_p95":0.17362,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25045,"mean_force":0.13602,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49956,0.03792,0.02622]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1680.0,"contact_point_centroid":[0.60444,0.17296,0.18331],"force_p95":0.07287,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24639,"mean_force":0.05142,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60864,0.15444,0.18022]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5215.0,"contact_point_centroid":[0.49971,0.01881,0.02661],"force_p95":0.0654,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19478,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49831,0.03782,0.02488]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1680.0,"contact_point_centroid":[0.61267,0.13563,0.18092],"force_p95":0.07364,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17111,"mean_force":0.05111,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60864,0.15444,0.18022]},{"body_a":"world","body_b":"grasp_target","contact_count":924.0,"contact_point_centroid":[0.51251,0.03972,-0.00186],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12316,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5028,0.01471,0.23273]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4405.0,"contact_point_centroid":[0.5573,0.07113,0.22984],"force_p95":0.09075,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13706,"mean_force":0.05317,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55445,0.08999,0.22848]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3946.0,"contact_point_centroid":[0.55428,0.11139,0.23007],"force_p95":0.09242,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12792,"mean_force":0.05704,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55663,0.09251,0.22716]},{"body_a":"world","body_b":"grasp_target","contact_count":1664.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50548,0.03509,0.09421]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4277.0,"contact_point_centroid":[0.49874,0.0572,0.02767],"force_p95":0.08313,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09541,"mean_force":0.05193,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49831,0.03782,0.02489]}],"total_contact_groups":12},"final_pose_error":0.02779,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62002,0.16594,0.14748],"final_tcp_position":[0.61652,0.16456,0.15665],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.70997,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":232.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":924.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50722,0.03191,0.15698],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1313,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":416.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1664.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.50701,0.0385,0.03429],"tcp_start":[0.50722,0.03191,0.15698],"tcp_to_object_dist_end":0.01001,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51245,0.03831,0.0254],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21348,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.16929,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11292.0,"raw_peak_contact_force":0.25045,"tcp_end":[0.49828,0.03782,0.02485],"tcp_start":[0.50701,0.0385,0.03429],"tcp_to_object_dist_end":0.0142,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":937.0,"n_steps_budget":1000.0,"object_pos_end":[0.5217,0.03898,0.2515],"object_pos_start":[0.51245,0.03831,0.0254],"object_to_goal_dist_end":0.20094,"object_to_goal_dist_start":0.21348,"object_z_max":0.25127,"peak_contact_force":0.08055,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":35430.0,"raw_peak_contact_force":0.70997,"subtask_id":"lift_object","tcp_end":[0.50895,0.03805,0.25776],"tcp_start":[0.49828,0.03782,0.02485],"tcp_to_object_dist_end":0.01424,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":215.0,"n_steps_budget":1000.0,"object_pos_end":[0.604,0.14695,0.19057],"object_pos_start":[0.5217,0.03898,0.2515],"object_to_goal_dist_end":0.0573,"object_to_goal_dist_start":0.20094,"object_z_max":0.2517,"peak_contact_force":0.07295,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8351.0,"raw_peak_contact_force":0.13706,"tcp_end":[0.60346,0.14648,0.19951],"tcp_start":[0.50895,0.03805,0.25776],"tcp_to_object_dist_end":0.00896,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":84.0,"n_steps_budget":1000.0,"object_pos_end":[0.62002,0.16594,0.14748],"object_pos_start":[0.604,0.14695,0.19057],"object_to_goal_dist_end":0.01031,"object_to_goal_dist_start":0.0573,"object_z_max":0.19057,"peak_contact_force":0.0713,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3360.0,"raw_peak_contact_force":0.24639,"subtask_id":"place_goal","tcp_end":[0.61652,0.16456,0.15665],"tcp_start":[0.60346,0.14648,0.19951],"tcp_to_object_dist_end":0.00992,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0033,"average_solve_count":303.0,"average_success_count":303.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_tolerance":0.03585,"approach_1.speed":0.08128,"descend_1.descend_tolerance":0.01029,"descend_1.speed":0.02768,"descend_2.descend_tolerance":0.00992,"descend_2.descend_x_offset":5e-05,"descend_2.descend_y_offset":-0.00779,"descend_2.descend_z_offset":0.00499,"descend_2.speed":0.02381,"lift_1.lift_height":0.21266,"lift_1.lift_speed":0.05563,"lift_1.lift_tolerance":0.02859,"transport_1.speed":0.1179,"transport_1.transport_tolerance":0.01728},"optimized_scores":{"best_composite_score":0.15897,"best_fitness_score":0.97897,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":72.0,"contact_point_centroid":[0.47992,0.04589,-0.00172],"force_p95":0.54601,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60941,"mean_force":0.24553,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4688,0.04621,0.02758]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7046.0,"contact_point_centroid":[0.47159,0.06545,0.11752],"force_p95":0.08654,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28071,"mean_force":0.05901,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47221,0.04625,0.11502]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48285,0.04852,-0.00223],"force_p95":0.18713,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26594,"mean_force":0.14001,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47087,0.04644,0.02766]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8700.0,"contact_point_centroid":[0.47372,0.02728,0.11668],"force_p95":0.08354,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24921,"mean_force":0.04879,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47224,0.04625,0.11537]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5102.0,"contact_point_centroid":[0.47132,0.02734,0.02773],"force_p95":0.06753,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20743,"mean_force":0.04203,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46966,0.04632,0.02645]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2300.0,"contact_point_centroid":[0.56843,0.23682,0.25564],"force_p95":0.07014,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15594,"mean_force":0.04813,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57469,0.21895,0.25235]},{"body_a":"world","body_b":"grasp_target","contact_count":700.0,"contact_point_centroid":[0.4827,0.04873,-0.00182],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12333,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4925,0.01751,0.23521]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2300.0,"contact_point_centroid":[0.58068,0.20066,0.25283],"force_p95":0.07198,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13694,"mean_force":0.04877,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57469,0.21895,0.25235]},{"body_a":"world","body_b":"grasp_target","contact_count":1760.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47965,0.04211,0.09773]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14993.0,"contact_point_centroid":[0.53013,0.11541,0.23936],"force_p95":0.0766,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12046,"mean_force":0.04963,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52594,0.13403,0.23809]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13671.0,"contact_point_centroid":[0.52475,0.15732,0.24276],"force_p95":0.08042,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1056,"mean_force":0.05298,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5286,0.13875,0.23979]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4242.0,"contact_point_centroid":[0.4696,0.06572,0.02885],"force_p95":0.08806,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10132,"mean_force":0.05278,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46967,0.04632,0.02646]}],"total_contact_groups":12},"final_pose_error":0.00992,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.57868,0.22061,0.22544],"final_tcp_position":[0.57655,0.21928,0.23361],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.60941,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":176.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":700.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4845,0.03734,0.16394],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1384,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":440.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1760.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.47808,0.0471,0.03499],"tcp_start":[0.4845,0.03734,0.16394],"tcp_to_object_dist_end":0.01022,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48274,0.04693,0.02521],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29165,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.1811,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11144.0,"raw_peak_contact_force":0.26594,"tcp_end":[0.46963,0.04632,0.02642],"tcp_start":[0.47808,0.0471,0.03499],"tcp_to_object_dist_end":0.01318,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":401.0,"n_steps_budget":1000.0,"object_pos_end":[0.49146,0.04753,0.2077],"object_pos_start":[0.48274,0.04693,0.02521],"object_to_goal_dist_end":0.20389,"object_to_goal_dist_start":0.29165,"object_z_max":0.20725,"peak_contact_force":0.08557,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15818.0,"raw_peak_contact_force":0.60941,"subtask_id":"lift_object","tcp_end":[0.47852,0.04656,0.20996],"tcp_start":[0.46963,0.04632,0.02642],"tcp_to_object_dist_end":0.01317,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":733.0,"n_steps_budget":1000.0,"object_pos_end":[0.57582,0.21964,0.2617],"object_pos_start":[0.49146,0.04753,0.2077],"object_to_goal_dist_end":0.0331,"object_to_goal_dist_start":0.20389,"object_z_max":0.26164,"peak_contact_force":0.0715,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28664.0,"raw_peak_contact_force":0.12046,"tcp_end":[0.57405,0.21858,0.26914],"tcp_start":[0.47852,0.04656,0.20996],"tcp_to_object_dist_end":0.00772,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":115.0,"n_steps_budget":1000.0,"object_pos_end":[0.57868,0.22061,0.22544],"object_pos_start":[0.57582,0.21964,0.2617],"object_to_goal_dist_end":0.01018,"object_to_goal_dist_start":0.0331,"object_z_max":0.2617,"peak_contact_force":0.072,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4600.0,"raw_peak_contact_force":0.15594,"subtask_id":"place_goal","tcp_end":[0.57655,0.21928,0.23361],"tcp_start":[0.57405,0.21858,0.26914],"tcp_to_object_dist_end":0.00855,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.91123,"average_solve_count":383.0,"average_success_count":383.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_tolerance":0.024,"approach_1.speed":0.0674,"descend_1.descend_tolerance":0.01147,"descend_1.speed":0.02497,"descend_2.descend_tolerance":0.01706,"descend_2.descend_x_offset":0.0,"descend_2.descend_y_offset":0.00777,"descend_2.descend_z_offset":0.02305,"descend_2.speed":0.02387,"lift_1.lift_height":0.1408,"lift_1.lift_speed":0.01367,"lift_1.lift_tolerance":0.02909,"transport_1.speed":0.07463,"transport_1.transport_tolerance":0.02432},"optimized_scores":{"best_composite_score":0.15622,"best_fitness_score":0.97622,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":106.0,"contact_point_centroid":[0.53446,-0.0209,-0.0016],"force_p95":0.41241,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47184,"mean_force":0.20699,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52084,-0.02069,0.02583]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5971.0,"contact_point_centroid":[0.52516,-0.00176,0.07976],"force_p95":0.07761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21114,"mean_force":0.05019,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52435,-0.02078,0.07769]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4901.0,"contact_point_centroid":[0.52418,-0.04,0.08103],"force_p95":0.08228,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20735,"mean_force":0.0587,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52439,-0.02079,0.07818]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":740.0,"contact_point_centroid":[0.6109,0.19778,0.2369],"force_p95":0.09628,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2073,"mean_force":0.07068,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60317,0.21534,0.23627]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":822.0,"contact_point_centroid":[0.59949,0.23385,0.23849],"force_p95":0.08882,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1962,"mean_force":0.06258,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60319,0.21543,0.23614]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02129,-0.00205],"force_p95":0.13804,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17167,"mean_force":0.12661,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52322,-0.02072,0.02677]},{"body_a":"world","body_b":"grasp_target","contact_count":1064.0,"contact_point_centroid":[0.53702,-0.02132,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51272,-0.00851,0.22769]},{"body_a":"world","body_b":"grasp_target","contact_count":1448.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5277,-0.01929,0.09281]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11164.0,"contact_point_centroid":[0.56951,0.07764,0.19018],"force_p95":0.08856,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11703,"mean_force":0.06126,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56551,0.09637,0.18822]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12962.0,"contact_point_centroid":[0.56348,0.11386,0.18996],"force_p95":0.0785,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10662,"mean_force":0.05267,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5651,0.0951,0.18763]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5294.0,"contact_point_centroid":[0.52304,-0.00168,0.02768],"force_p95":0.06748,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1044,"mean_force":0.04092,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52194,-0.02071,0.02532]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4175.0,"contact_point_centroid":[0.52302,-0.04002,0.02799],"force_p95":0.07994,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09205,"mean_force":0.05204,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52194,-0.02071,0.02533]}],"total_contact_groups":12},"final_pose_error":0.01705,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61973,0.2267,0.22263],"final_tcp_position":[0.60438,0.22133,0.22782],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.47184,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":267.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1064.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.5278,-0.01783,0.15157],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12593,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":362.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1448.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.53087,-0.02082,0.03552],"tcp_start":[0.5278,-0.01783,0.15157],"tcp_to_object_dist_end":0.01133,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53689,-0.02103,0.02582],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31664,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13761,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11269.0,"raw_peak_contact_force":0.17167,"tcp_end":[0.52191,-0.02071,0.02529],"tcp_start":[0.53087,-0.02082,0.03552],"tcp_to_object_dist_end":0.01499,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":275.0,"n_steps_budget":1000.0,"object_pos_end":[0.54465,-0.02134,0.13863],"object_pos_start":[0.53689,-0.02103,0.02582],"object_to_goal_dist_end":0.26663,"object_to_goal_dist_start":0.31664,"object_z_max":0.13819,"peak_contact_force":0.08077,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10978.0,"raw_peak_contact_force":0.47184,"subtask_id":"lift_object","tcp_end":[0.53081,-0.02092,0.13833],"tcp_start":[0.52191,-0.02071,0.02529],"tcp_to_object_dist_end":0.01385,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":662.0,"n_steps_budget":1000.0,"object_pos_end":[0.61696,0.21597,0.23731],"object_pos_start":[0.54465,-0.02134,0.13863],"object_to_goal_dist_end":0.03281,"object_to_goal_dist_start":0.26663,"object_z_max":0.23717,"peak_contact_force":0.09437,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24126.0,"raw_peak_contact_force":0.11703,"tcp_end":[0.60264,0.21125,0.24166],"tcp_start":[0.53081,-0.02092,0.13833],"tcp_to_object_dist_end":0.01569,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":50.0,"n_steps_budget":1000.0,"object_pos_end":[0.61973,0.2267,0.22263],"object_pos_start":[0.61696,0.21597,0.23731],"object_to_goal_dist_end":0.01793,"object_to_goal_dist_start":0.03281,"object_z_max":0.23734,"peak_contact_force":0.09591,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1562.0,"raw_peak_contact_force":0.2073,"subtask_id":"place_goal","tcp_end":[0.60438,0.22133,0.22782],"tcp_start":[0.60264,0.21125,0.24166],"tcp_to_object_dist_end":0.01706,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```