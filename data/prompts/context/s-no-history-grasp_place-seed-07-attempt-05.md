## Search State

- **Seed**: 7
- **Iteration**: 6 / 15

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
| approach_1 | 1.00 | 1.00 | 0.1447 |
| descend_1 | 1.00 | 1.00 | 0.1273 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 0.00 | 1.00 | 0.1152 |
| transport_1 | 0.67 | 1.00 | 0.1974 |
| descend_2 | 1.00 | 1.00 | 0.0343 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, 0.017, 0.160) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 15.583 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.507, 0.017, 0.160)→(0.505, 0.022, 0.033) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 5.626 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.505, 0.022, 0.033)→(0.497, 0.021, 0.024) | (0.511, 0.022, 0.026)→(0.511, 0.021, 0.025) | 0.273→0.274 | 1.00 / 43.333 | 0.162 | 0.233 |
| lift_1 | lift | 0.00 / step_budget | (0.497, 0.021, 0.024)→(0.505, 0.021, 0.139) | (0.511, 0.021, 0.025)→(0.516, 0.021, 0.142) | 0.274→0.221 | 1.00 / 39.667 | 0.083 | 0.608 |
| transport_1 | approach | 0.67 / step_budget | (0.505, 0.021, 0.139)→(0.588, 0.177, 0.219) | (0.516, 0.021, 0.142)→(0.599, 0.179, 0.224) | 0.221→0.045 | 1.00 / 38.000 | 0.091 | 0.116 |
| descend_2 | descend | 1.00 / step_budget | (0.588, 0.177, 0.219)→(0.602, 0.195, 0.197) | (0.599, 0.179, 0.224)→(0.615, 0.199, 0.201) | 0.045→0.016 | 1.00 / 35.333 | 55983.967 | 0.184 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.111
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.651
- phase_breakdown.lift_object_score: 0.474
- phase_breakdown.place_goal_score: 0.723
- phase_breakdown.reach_object_score: 0.431
- phase_breakdown.grasp_contact_score: 0.903
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
- **Final σ (mean)**: 0.306


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.69377,"average_solve_count":369.0,"average_success_count":369.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_tolerance":0.03089,"approach_1.speed":0.06836,"descend_1.descend_tolerance":0.00988,"descend_1.speed":0.02458,"descend_2.descend_tolerance":0.02233,"descend_2.descend_x_offset":0.01456,"descend_2.descend_y_offset":-0.00432,"descend_2.descend_z_offset":-0.00047,"descend_2.speed":0.01268,"lift_1.lift_height":0.18151,"lift_1.lift_speed":0.05089,"lift_1.lift_tolerance":0.06094,"transport_1.speed":0.13315,"transport_1.transport_tolerance":0.04321},"optimized_scores":{"best_composite_score":0.15744,"best_fitness_score":0.97744,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":73.0,"contact_point_centroid":[0.50986,0.03786,-0.0017],"force_p95":0.55836,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61182,"mean_force":0.26391,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49746,0.03771,0.0256]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2277.0,"contact_point_centroid":[0.50027,0.05692,0.0798],"force_p95":0.10362,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27105,"mean_force":0.06298,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50071,0.0377,0.0773]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51262,0.03955,-0.00218],"force_p95":0.17489,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25649,"mean_force":0.13638,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49958,0.03791,0.02599]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2800.0,"contact_point_centroid":[0.50166,0.01869,0.07862],"force_p95":0.09741,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24143,"mean_force":0.05262,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50073,0.0377,0.07738]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5215.0,"contact_point_centroid":[0.49973,0.0188,0.02637],"force_p95":0.06518,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19782,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49833,0.03781,0.02464]},{"body_a":"world","body_b":"grasp_target","contact_count":824.0,"contact_point_centroid":[0.51251,0.03972,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12322,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5031,0.01487,0.23221]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2340.0,"contact_point_centroid":[0.60525,0.16863,0.16564],"force_p95":0.07444,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13304,"mean_force":0.04969,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60927,0.15009,0.16254]},{"body_a":"world","body_b":"grasp_target","contact_count":1748.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5055,0.0349,0.09473]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3775.0,"contact_point_centroid":[0.55522,0.06959,0.16344],"force_p95":0.08161,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12152,"mean_force":0.05115,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55267,0.08851,0.16219]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2340.0,"contact_point_centroid":[0.61319,0.13124,0.16322],"force_p95":0.07818,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11574,"mean_force":0.0494,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60927,0.15009,0.16254]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3314.0,"contact_point_centroid":[0.5532,0.11063,0.1658],"force_p95":0.08357,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10453,"mean_force":0.05586,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55543,0.09173,0.16299]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4279.0,"contact_point_centroid":[0.49875,0.05718,0.02743],"force_p95":0.08343,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09605,"mean_force":0.05191,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49834,0.03781,0.02465]}],"total_contact_groups":12},"final_pose_error":0.0222,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.6325,0.16014,0.14523],"final_tcp_position":[0.62388,0.15867,0.14287],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":46.5044,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":207.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":46.5044,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":824.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50732,0.03153,0.15868],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":437.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1748.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.50702,0.03848,0.03404],"tcp_start":[0.50732,0.03153,0.15868],"tcp_to_object_dist_end":0.0098,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51246,0.0383,0.02538],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.2135,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.17038,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11294.0,"raw_peak_contact_force":0.25649,"tcp_end":[0.4983,0.0378,0.02461],"tcp_start":[0.50702,0.03848,0.03404],"tcp_to_object_dist_end":0.01419,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":128.0,"n_steps_budget":1000.0,"object_pos_end":[0.51958,0.03847,0.14931],"object_pos_start":[0.51246,0.0383,0.02538],"object_to_goal_dist_end":0.17219,"object_to_goal_dist_start":0.2135,"object_z_max":0.1482,"peak_contact_force":0.08667,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5150.0,"raw_peak_contact_force":0.61182,"subtask_id":"lift_object","tcp_end":[0.50715,0.03794,0.14725],"tcp_start":[0.4983,0.0378,0.02461],"tcp_to_object_dist_end":0.01261,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":181.0,"n_steps_budget":1000.0,"object_pos_end":[0.60647,0.14449,0.18013],"object_pos_start":[0.51958,0.03847,0.14931],"object_to_goal_dist_end":0.04963,"object_to_goal_dist_start":0.17219,"object_z_max":0.17996,"peak_contact_force":0.07827,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7089.0,"raw_peak_contact_force":0.12152,"tcp_end":[0.60076,0.14377,0.1775],"tcp_start":[0.50715,0.03794,0.14725],"tcp_to_object_dist_end":0.00633,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":117.0,"n_steps_budget":1000.0,"object_pos_end":[0.6325,0.16014,0.14523],"object_pos_start":[0.60647,0.14449,0.18013],"object_to_goal_dist_end":0.01333,"object_to_goal_dist_start":0.04963,"object_z_max":0.18027,"peak_contact_force":0.07907,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4680.0,"raw_peak_contact_force":0.13304,"subtask_id":"place_goal","tcp_end":[0.62388,0.15867,0.14287],"tcp_start":[0.60076,0.14377,0.1775],"tcp_to_object_dist_end":0.00906,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.91731,"average_solve_count":387.0,"average_success_count":387.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_tolerance":0.04282,"approach_1.speed":0.0732,"descend_1.descend_tolerance":0.00748,"descend_1.speed":0.02225,"descend_2.descend_tolerance":0.01883,"descend_2.descend_x_offset":0.00761,"descend_2.descend_y_offset":-0.00351,"descend_2.descend_z_offset":0.00858,"descend_2.speed":0.02865,"lift_1.lift_height":0.18735,"lift_1.lift_speed":0.05544,"lift_1.lift_tolerance":0.07008,"transport_1.speed":0.04313,"transport_1.transport_tolerance":0.03662},"optimized_scores":{"best_composite_score":0.1592,"best_fitness_score":0.9792,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":71.0,"contact_point_centroid":[0.4802,0.04644,-0.0018],"force_p95":0.64264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71398,"mean_force":0.32087,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46877,0.04639,0.02413]},{"body_a":"grasp_target","body_b":"hand","contact_count":110.0,"contact_point_centroid":[0.49869,0.0664,0.10647],"force_p95":0.25174,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38742,"mean_force":0.08192,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47166,0.04638,0.07282]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1985.0,"contact_point_centroid":[0.47071,0.06552,0.07512],"force_p95":0.1107,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2725,"mean_force":0.06302,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47165,0.04637,0.07286]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48273,0.04839,-0.00229],"force_p95":0.18458,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27105,"mean_force":0.14428,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47084,0.04663,0.02427]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2254.0,"contact_point_centroid":[0.47351,0.02736,0.0737],"force_p95":0.09864,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23222,"mean_force":0.05601,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47164,0.04638,0.07241]},{"body_a":"grasp_target","body_b":"hand","contact_count":349.0,"contact_point_centroid":[0.49905,0.05432,0.05544],"force_p95":0.12985,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22409,"mean_force":0.03829,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46982,0.04653,0.02325]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5094.0,"contact_point_centroid":[0.47115,0.02753,0.02432],"force_p95":0.06815,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16191,"mean_force":0.04139,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46961,0.04651,0.02305]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":983.0,"contact_point_centroid":[0.56634,0.22879,0.25346],"force_p95":0.09086,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14852,"mean_force":0.06201,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57117,0.21044,0.24892]},{"body_a":"world","body_b":"grasp_target","contact_count":588.0,"contact_point_centroid":[0.4827,0.04873,-0.00178],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12346,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49337,0.01645,0.23926]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1218.0,"contact_point_centroid":[0.57774,0.19258,0.24964],"force_p95":0.08241,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12407,"mean_force":0.05126,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57118,0.21045,0.24888]},{"body_a":"world","body_b":"grasp_target","contact_count":2388.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48008,0.0415,0.0973]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4306.0,"contact_point_centroid":[0.46937,0.06593,0.02538],"force_p95":0.08691,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10676,"mean_force":0.05264,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46963,0.04651,0.02306]},{"body_a":"grasp_target","body_b":"hand","contact_count":91.0,"contact_point_centroid":[0.51054,0.08508,0.1933],"force_p95":0.09374,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10389,"mean_force":0.04625,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48857,0.06426,0.15749]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6099.0,"contact_point_centroid":[0.51826,0.14365,0.20131],"force_p95":0.08344,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10029,"mean_force":0.05767,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52146,0.12487,0.19816]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7643.0,"contact_point_centroid":[0.52561,0.10712,0.19996],"force_p95":0.0787,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09624,"mean_force":0.04808,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52197,0.12579,0.1988]}],"total_contact_groups":15},"final_pose_error":0.01845,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.59184,0.22007,0.24229],"final_tcp_position":[0.57675,0.21546,0.23804],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":16.63233,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":148.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":588.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.48576,0.0357,0.1699],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1445,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":597.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":16.63233,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2388.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_contact","tcp_end":[0.47802,0.0473,0.0315],"tcp_start":[0.48576,0.0357,0.1699],"tcp_to_object_dist_end":0.00735,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48245,0.04703,0.02507],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29179,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.17862,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11549.0,"raw_peak_contact_force":0.27105,"tcp_end":[0.46959,0.0465,0.02303],"tcp_start":[0.47802,0.0473,0.0315],"tcp_to_object_dist_end":0.01303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":110.0,"n_steps_budget":1000.0,"object_pos_end":[0.48853,0.04716,0.14651],"object_pos_start":[0.48245,0.04703,0.02507],"object_to_goal_dist_end":0.22086,"object_to_goal_dist_start":0.29179,"object_z_max":0.1452,"peak_contact_force":0.08478,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4420.0,"raw_peak_contact_force":0.71398,"subtask_id":"lift_object","tcp_end":[0.47803,0.04667,0.14301],"tcp_start":[0.46959,0.0465,0.02303],"tcp_to_object_dist_end":0.01108,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":354.0,"n_steps_budget":1000.0,"object_pos_end":[0.57993,0.20962,0.26086],"object_pos_start":[0.48853,0.04716,0.14651],"object_to_goal_dist_end":0.036,"object_to_goal_dist_start":0.22086,"object_z_max":0.26053,"peak_contact_force":0.08344,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13833.0,"raw_peak_contact_force":0.10389,"tcp_end":[0.5674,0.20605,0.2563],"tcp_start":[0.47803,0.04667,0.14301],"tcp_to_object_dist_end":0.0138,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":60.0,"n_steps_budget":1000.0,"object_pos_end":[0.59184,0.22007,0.24229],"object_pos_start":[0.57993,0.20962,0.26086],"object_to_goal_dist_end":0.01777,"object_to_goal_dist_start":0.036,"object_z_max":0.26121,"peak_contact_force":0.0921,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2201.0,"raw_peak_contact_force":0.14852,"subtask_id":"place_goal","tcp_end":[0.57675,0.21546,0.23804],"tcp_start":[0.5674,0.20605,0.2563],"tcp_to_object_dist_end":0.01634,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.98674,"average_solve_count":377.0,"average_success_count":377.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_tolerance":0.02514,"approach_1.speed":0.03309,"descend_1.descend_tolerance":0.01086,"descend_1.speed":0.03458,"descend_2.descend_tolerance":0.01429,"descend_2.descend_x_offset":0.00053,"descend_2.descend_y_offset":-0.00491,"descend_2.descend_z_offset":0.01917,"descend_2.speed":0.03812,"lift_1.lift_height":0.17351,"lift_1.lift_speed":0.02534,"lift_1.lift_tolerance":0.08504,"transport_1.speed":0.12537,"transport_1.transport_tolerance":0.06112},"optimized_scores":{"best_composite_score":0.1562,"best_fitness_score":0.9762,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":94.0,"contact_point_centroid":[0.53421,-0.02086,-0.00157],"force_p95":0.46895,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4988,"mean_force":0.23872,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52091,-0.0207,0.02518]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1665.0,"contact_point_centroid":[0.6075,0.17883,0.21953],"force_p95":0.11158,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27188,"mean_force":0.08554,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59875,0.19614,0.21723]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2624.0,"contact_point_centroid":[0.52307,-0.00175,0.06273],"force_p95":0.09647,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21817,"mean_force":0.0546,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52266,-0.02077,0.06125]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2129.0,"contact_point_centroid":[0.52162,-0.03998,0.06418],"force_p95":0.11124,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21586,"mean_force":0.06356,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52268,-0.02077,0.06156]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02129,-0.00205],"force_p95":0.13781,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17033,"mean_force":0.12654,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52325,-0.02073,0.02606]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2309.0,"contact_point_centroid":[0.59602,0.21558,0.22083],"force_p95":0.10486,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16732,"mean_force":0.06252,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59913,0.19737,0.21662]},{"body_a":"world","body_b":"grasp_target","contact_count":1056.0,"contact_point_centroid":[0.53702,-0.02132,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51239,-0.00831,0.22936]},{"body_a":"world","body_b":"grasp_target","contact_count":1488.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52764,-0.01923,0.09261]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3781.0,"contact_point_centroid":[0.56303,0.0525,0.17467],"force_p95":0.09277,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12231,"mean_force":0.05938,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56019,0.07144,0.17236]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4277.0,"contact_point_centroid":[0.55933,0.09277,0.17601],"force_p95":0.07735,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10395,"mean_force":0.04964,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56094,0.07394,0.17347]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5294.0,"contact_point_centroid":[0.52306,-0.00168,0.02697],"force_p95":0.06754,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10389,"mean_force":0.04092,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52196,-0.02071,0.02462]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4174.0,"contact_point_centroid":[0.52304,-0.04002,0.02729],"force_p95":0.07991,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09223,"mean_force":0.05205,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52196,-0.02071,0.02462]}],"total_contact_groups":12},"final_pose_error":0.01417,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.62047,0.21685,0.21404],"final_tcp_position":[0.60398,0.21197,0.21064],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":265.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1056.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52763,-0.0177,0.15262],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.127,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":372.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1488.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.53089,-0.02082,0.03479],"tcp_start":[0.52763,-0.0177,0.15262],"tcp_to_object_dist_end":0.01071,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53688,-0.02103,0.02582],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31664,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13742,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11268.0,"raw_peak_contact_force":0.17033,"tcp_end":[0.52193,-0.02071,0.02458],"tcp_start":[0.53089,-0.02082,0.03479],"tcp_to_object_dist_end":0.01501,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":120.0,"n_steps_budget":1000.0,"object_pos_end":[0.54059,-0.02122,0.1308],"object_pos_start":[0.53688,-0.02103,0.02582],"object_to_goal_dist_end":0.26966,"object_to_goal_dist_start":0.31664,"object_z_max":0.12946,"peak_contact_force":0.07844,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4847.0,"raw_peak_contact_force":0.4988,"subtask_id":"lift_object","tcp_end":[0.52953,-0.02092,0.12675],"tcp_start":[0.52193,-0.02071,0.02458],"tcp_to_object_dist_end":0.01178,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":207.0,"n_steps_budget":1000.0,"object_pos_end":[0.61035,0.1834,0.2303],"object_pos_start":[0.54059,-0.02122,0.1308],"object_to_goal_dist_end":0.04991,"object_to_goal_dist_start":0.26966,"object_z_max":0.22981,"peak_contact_force":0.1107,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8058.0,"raw_peak_contact_force":0.12231,"tcp_end":[0.59476,0.17985,0.22461],"tcp_start":[0.52953,-0.02092,0.12675],"tcp_to_object_dist_end":0.01697,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":138.0,"n_steps_budget":1000.0,"object_pos_end":[0.62047,0.21685,0.21404],"object_pos_start":[0.61035,0.1834,0.2303],"object_to_goal_dist_end":0.01631,"object_to_goal_dist_start":0.04991,"object_z_max":0.23117,"peak_contact_force":167951.73011,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3974.0,"raw_peak_contact_force":0.27188,"subtask_id":"place_goal","tcp_end":[0.60398,0.21197,0.21064],"tcp_start":[0.59476,0.17985,0.22461],"tcp_to_object_dist_end":0.01753,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```