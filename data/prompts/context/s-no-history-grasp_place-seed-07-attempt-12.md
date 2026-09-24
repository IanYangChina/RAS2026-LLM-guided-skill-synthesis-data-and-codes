## Search State

- **Seed**: 7
- **Iteration**: 13 / 15

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

## Current Skill (Q=0.157) — your mutation base

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

- **Composite score**: 0.157
- **task_score** (E): 1.000
- **fitness_score**: 0.977  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.820

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.1069 |
| descend_1 | 1.00 | 1.00 | 0.1612 |
| grasp_1 | 1.00 | 1.00 | 0.0129 |
| lift_1 | 0.67 | 1.00 | 0.1188 |
| transport_1 | 0.67 | 1.00 | 0.2026 |
| descend_2 | 1.00 | 1.00 | 0.0341 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, 0.011, 0.197) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.122 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.508, 0.011, 0.197)→(0.506, 0.021, 0.037) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 27.129 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.021, 0.037)→(0.497, 0.021, 0.027) | (0.511, 0.022, 0.026)→(0.511, 0.021, 0.025) | 0.273→0.274 | 1.00 / 42.000 | 0.178 | 0.256 |
| lift_1 | lift | 0.67 / step_budget | (0.497, 0.021, 0.027)→(0.505, 0.021, 0.146) | (0.511, 0.021, 0.025)→(0.518, 0.021, 0.145) | 0.274→0.220 | 1.00 / 39.000 | 0.086 | 0.602 |
| transport_1 | approach | 0.67 / step_budget | (0.505, 0.021, 0.146)→(0.592, 0.182, 0.222) | (0.518, 0.021, 0.145)→(0.608, 0.187, 0.220) | 0.220→0.037 | 1.00 / 32.333 | 0.094 | 0.117 |
| descend_2 | descend | 1.00 / step_budget | (0.592, 0.182, 0.222)→(0.603, 0.198, 0.197) | (0.608, 0.187, 0.220)→(0.620, 0.203, 0.193) | 0.037→0.016 | 1.00 / 29.000 | 0.105 | 0.240 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.105
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.587
- phase_breakdown.lift_object_score: 0.515
- phase_breakdown.place_goal_score: 0.691
- phase_breakdown.reach_object_score: 0.207
- phase_breakdown.grasp_contact_score: 0.831
- grasp_place_fitness: 0.979

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.979
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.158
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.277


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.76044,"average_solve_count":455.0,"average_success_count":455.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_tolerance":0.07555,"approach_1.speed":0.03859,"descend_1.descend1_tolerance":0.00552,"descend_1.speed":0.02638,"descend_2.descend_tolerance":0.02792,"descend_2.descend_x_offset":0.01258,"descend_2.descend_y_offset":-0.00245,"descend_2.descend_z_offset":-0.00831,"descend_2.speed":0.01839,"lift_1.lift_height":0.17008,"lift_1.lift_speed":0.04242,"lift_1.lift_tolerance":0.04673,"transport_1.speed":0.04044,"transport_1.transport_tolerance":0.01903},"optimized_scores":{"best_composite_score":0.15763,"best_fitness_score":0.97763,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.51011,0.03727,-0.0018],"force_p95":0.53179,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58306,"mean_force":0.25851,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49762,0.03725,0.02486]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51266,0.0395,-0.00224],"force_p95":0.18857,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27293,"mean_force":0.14024,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49979,0.03745,0.02535]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3026.0,"contact_point_centroid":[0.50042,0.05647,0.08276],"force_p95":0.08965,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25023,"mean_force":0.06081,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50085,0.03726,0.08025]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3718.0,"contact_point_centroid":[0.50181,0.01824,0.08156],"force_p95":0.08606,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.223,"mean_force":0.05056,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50086,0.03726,0.08029]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5178.0,"contact_point_centroid":[0.4999,0.01839,0.0257],"force_p95":0.06518,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19823,"mean_force":0.04124,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49853,0.03735,0.02399]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1255.0,"contact_point_centroid":[0.61584,0.18271,0.17459],"force_p95":0.09404,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15535,"mean_force":0.05988,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61899,0.16402,0.17092]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1455.0,"contact_point_centroid":[0.62425,0.14572,0.17141],"force_p95":0.07976,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13968,"mean_force":0.05224,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61897,0.16401,0.17101]},{"body_a":"world","body_b":"grasp_target","contact_count":376.0,"contact_point_centroid":[0.51251,0.03972,-0.00167],"force_p95":0.13823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.124,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50281,0.00793,0.26381]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50583,0.02998,0.11267]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13146.0,"contact_point_centroid":[0.56422,0.0823,0.16642],"force_p95":0.07998,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10482,"mean_force":0.05001,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56106,0.10106,0.16506]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10744.0,"contact_point_centroid":[0.56024,0.12138,0.16895],"force_p95":0.08259,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09793,"mean_force":0.05869,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56229,0.10246,0.16547]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4153.0,"contact_point_centroid":[0.49915,0.05677,0.02679],"force_p95":0.08851,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09688,"mean_force":0.05389,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49854,0.03735,0.02401]},{"body_a":"grasp_target","body_b":"hand","contact_count":64.0,"contact_point_centroid":[0.5229,0.05645,0.08247],"force_p95":0.02818,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.02935,"mean_force":0.01633,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49781,0.03713,0.04851]}],"total_contact_groups":13},"final_pose_error":0.02766,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.64206,0.1699,0.14826],"final_tcp_position":[0.62566,0.16595,0.14991],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.58306,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":95.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02601],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21223,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12215,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":376.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50838,0.02171,0.20254],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1775,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02601],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_contact","tcp_end":[0.5071,0.038,0.03323],"tcp_start":[0.50838,0.02171,0.20254],"tcp_to_object_dist_end":0.00917,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5125,0.03785,0.0252],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21386,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.18232,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11131.0,"raw_peak_contact_force":0.27293,"tcp_end":[0.4985,0.03734,0.02396],"tcp_start":[0.5071,0.038,0.03323],"tcp_to_object_dist_end":0.01406,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":170.0,"n_steps_budget":1000.0,"object_pos_end":[0.51933,0.03803,0.15237],"object_pos_start":[0.5125,0.03785,0.0252],"object_to_goal_dist_end":0.17279,"object_to_goal_dist_start":0.21386,"object_z_max":0.15155,"peak_contact_force":0.08679,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6887.0,"raw_peak_contact_force":0.58306,"subtask_id":"lift_object","tcp_end":[0.50695,0.03748,0.14968],"tcp_start":[0.4985,0.03734,0.02396],"tcp_to_object_dist_end":0.01268,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":632.0,"n_steps_budget":1000.0,"object_pos_end":[0.62917,0.16572,0.18302],"object_pos_start":[0.51933,0.03803,0.15237],"object_to_goal_dist_end":0.03863,"object_to_goal_dist_start":0.17279,"object_z_max":0.18298,"peak_contact_force":0.08201,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23890.0,"raw_peak_contact_force":0.10482,"tcp_end":[0.61603,0.1627,0.18372],"tcp_start":[0.50695,0.03748,0.14968],"tcp_to_object_dist_end":0.0135,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":75.0,"n_steps_budget":1000.0,"object_pos_end":[0.64206,0.1699,0.14826],"object_pos_start":[0.62917,0.16572,0.18302],"object_to_goal_dist_end":0.01508,"object_to_goal_dist_start":0.03863,"object_z_max":0.18302,"peak_contact_force":0.10008,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2710.0,"raw_peak_contact_force":0.15535,"subtask_id":"place_goal","tcp_end":[0.62566,0.16595,0.14991],"tcp_start":[0.61603,0.1627,0.18372],"tcp_to_object_dist_end":0.01695,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09422,"average_solve_count":329.0,"average_success_count":329.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_tolerance":0.08048,"approach_1.speed":0.05734,"descend_1.descend1_tolerance":0.01294,"descend_1.speed":0.03349,"descend_2.descend_tolerance":0.03076,"descend_2.descend_x_offset":0.01405,"descend_2.descend_y_offset":-0.00229,"descend_2.descend_z_offset":-0.00611,"descend_2.speed":0.02824,"lift_1.lift_height":0.16132,"lift_1.lift_speed":0.05557,"lift_1.lift_tolerance":0.03973,"transport_1.speed":0.0892,"transport_1.transport_tolerance":0.04542},"optimized_scores":{"best_composite_score":0.15904,"best_fitness_score":0.97904,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":71.0,"contact_point_centroid":[0.4804,0.04594,-0.00189],"force_p95":0.49942,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57689,"mean_force":0.24379,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46969,0.04526,0.03049]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3282.0,"contact_point_centroid":[0.47167,0.06457,0.08711],"force_p95":0.08964,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29191,"mean_force":0.06041,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47249,0.0454,0.08469]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4829,0.04847,-0.00233],"force_p95":0.21037,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28525,"mean_force":0.1464,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47172,0.04548,0.03058]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":809.0,"contact_point_centroid":[0.56443,0.22232,0.25018],"force_p95":0.11362,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24819,"mean_force":0.071,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.56839,0.20377,0.24541]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3871.0,"contact_point_centroid":[0.47409,0.0264,0.08668],"force_p95":0.08956,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23957,"mean_force":0.05171,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47258,0.04541,0.08554]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5169.0,"contact_point_centroid":[0.47188,0.02638,0.03054],"force_p95":0.0702,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20527,"mean_force":0.04146,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47052,0.04537,0.02936]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":970.0,"contact_point_centroid":[0.57565,0.18611,0.24665],"force_p95":0.09539,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17221,"mean_force":0.05929,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.56843,0.2038,0.24534]},{"body_a":"world","body_b":"grasp_target","contact_count":312.0,"contact_point_centroid":[0.4827,0.04873,-0.0016],"force_p95":0.13827,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12438,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49731,0.00989,0.26367]},{"body_a":"world","body_b":"grasp_target","contact_count":1724.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12259,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48378,0.03653,0.11441]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5494.0,"contact_point_centroid":[0.52319,0.10184,0.19865],"force_p95":0.08209,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11485,"mean_force":0.05028,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51944,0.1205,0.19733]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4387.0,"contact_point_centroid":[0.5166,0.1393,0.20054],"force_p95":0.08619,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10471,"mean_force":0.05943,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51941,0.12045,0.19731]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4299.0,"contact_point_centroid":[0.47046,0.06485,0.03191],"force_p95":0.09225,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09962,"mean_force":0.0528,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47053,0.04537,0.02938]}],"total_contact_groups":12},"final_pose_error":0.03014,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.59556,0.21739,0.22926],"final_tcp_position":[0.57692,0.21109,0.23193],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.57689,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":79.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02595],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.29002,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12221,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":312.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49289,0.02616,0.2048],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18056,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":431.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02595],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.29002,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1724.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_contact","tcp_end":[0.47901,0.04611,0.03805],"tcp_start":[0.49289,0.02616,0.2048],"tcp_to_object_dist_end":0.01286,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48281,0.04626,0.02488],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29227,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.20178,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11268.0,"raw_peak_contact_force":0.28525,"tcp_end":[0.47049,0.04536,0.02934],"tcp_start":[0.47901,0.04611,0.03805],"tcp_to_object_dist_end":0.01313,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":183.0,"n_steps_budget":1000.0,"object_pos_end":[0.48915,0.04668,0.14346],"object_pos_start":[0.48281,0.04626,0.02488],"object_to_goal_dist_end":0.22217,"object_to_goal_dist_start":0.29227,"object_z_max":0.14278,"peak_contact_force":0.08704,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7224.0,"raw_peak_contact_force":0.57689,"subtask_id":"lift_object","tcp_end":[0.47753,0.04576,0.1474],"tcp_start":[0.47049,0.04536,0.02934],"tcp_to_object_dist_end":0.0123,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":257.0,"n_steps_budget":1000.0,"object_pos_end":[0.57938,0.2037,0.24937],"object_pos_start":[0.48915,0.04668,0.14346],"object_to_goal_dist_end":0.03155,"object_to_goal_dist_start":0.22217,"object_z_max":0.24894,"peak_contact_force":0.08859,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9881.0,"raw_peak_contact_force":0.11485,"tcp_end":[0.56397,0.19892,0.25173],"tcp_start":[0.47753,0.04576,0.1474],"tcp_to_object_dist_end":0.01631,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":54.0,"n_steps_budget":1000.0,"object_pos_end":[0.59556,0.21739,0.22926],"object_pos_start":[0.57938,0.2037,0.24937],"object_to_goal_dist_end":0.0179,"object_to_goal_dist_start":0.03155,"object_z_max":0.25002,"peak_contact_force":0.10709,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1779.0,"raw_peak_contact_force":0.24819,"subtask_id":"place_goal","tcp_end":[0.57692,0.21109,0.23193],"tcp_start":[0.56397,0.19892,0.25173],"tcp_to_object_dist_end":0.01986,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0049,"average_solve_count":408.0,"average_success_count":408.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_tolerance":0.05749,"approach_1.speed":0.03185,"descend_1.descend1_tolerance":0.01509,"descend_1.speed":0.03493,"descend_2.descend_tolerance":0.01122,"descend_2.descend_x_offset":0.00308,"descend_2.descend_y_offset":-0.00309,"descend_2.descend_z_offset":0.01635,"descend_2.speed":0.0231,"lift_1.lift_height":0.17214,"lift_1.lift_speed":0.08434,"lift_1.lift_tolerance":0.05816,"transport_1.speed":0.02726,"transport_1.transport_tolerance":0.05288},"optimized_scores":{"best_composite_score":0.15485,"best_fitness_score":0.97485,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":65.0,"contact_point_centroid":[0.53342,-0.02044,-0.00157],"force_p95":0.56512,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64643,"mean_force":0.35008,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52054,-0.02023,0.03019]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.52298,-0.0396,0.08049],"force_p95":0.14604,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38062,"mean_force":0.07185,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52355,-0.02036,0.07778]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2750.0,"contact_point_centroid":[0.60016,0.22199,0.21974],"force_p95":0.11227,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31695,"mean_force":0.08345,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60137,0.20319,0.21634]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2590.0,"contact_point_centroid":[0.52446,-0.00142,0.08008],"force_p95":0.12325,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30681,"mean_force":0.05927,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52361,-0.02037,0.07824]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2555.0,"contact_point_centroid":[0.61085,0.18659,0.21752],"force_p95":0.11421,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28225,"mean_force":0.08714,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60147,0.20343,0.2162]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53709,-0.02129,-0.00209],"force_p95":0.15075,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20973,"mean_force":0.12989,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52287,-0.02026,0.03067]},{"body_a":"world","body_b":"grasp_target","contact_count":496.0,"contact_point_centroid":[0.53702,-0.02132,-0.00175],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12361,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50945,-0.00542,0.25365]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4794.0,"contact_point_centroid":[0.5234,-0.00133,0.03064],"force_p95":0.06982,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13111,"mean_force":0.04464,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5216,-0.02024,0.02923]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3631.0,"contact_point_centroid":[0.56329,0.04956,0.18132],"force_p95":0.10949,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13048,"mean_force":0.07502,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55849,0.0681,0.17853]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4435.0,"contact_point_centroid":[0.55837,0.08575,0.1808],"force_p95":0.09827,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12609,"mean_force":0.06113,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55813,0.06695,0.17804]},{"body_a":"world","body_b":"grasp_target","contact_count":1368.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52567,-0.01714,0.10827]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4117.0,"contact_point_centroid":[0.52298,-0.03949,0.03204],"force_p95":0.08894,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09388,"mean_force":0.0553,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5216,-0.02024,0.02924]}],"total_contact_groups":12},"final_pose_error":0.01119,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.6235,0.22313,0.20009],"final_tcp_position":[0.60727,0.21735,0.20791],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":125.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12257,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":496.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52417,-0.01385,0.18428],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15895,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":342.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1368.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_contact","tcp_end":[0.53061,-0.02033,0.03964],"tcp_start":[0.52417,-0.01385,0.18428],"tcp_to_object_dist_end":0.01509,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53707,-0.02071,0.02567],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31643,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14984,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10711.0,"raw_peak_contact_force":0.20973,"tcp_end":[0.52157,-0.02024,0.0292],"tcp_start":[0.53061,-0.02033,0.03964],"tcp_to_object_dist_end":0.0159,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":121.0,"n_steps_budget":1000.0,"object_pos_end":[0.54531,-0.02094,0.13849],"object_pos_start":[0.53707,-0.02071,0.02567],"object_to_goal_dist_end":0.26613,"object_to_goal_dist_start":0.31643,"object_z_max":0.13744,"peak_contact_force":0.08485,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4707.0,"raw_peak_contact_force":0.64643,"subtask_id":"lift_object","tcp_end":[0.53061,-0.02056,0.14099],"tcp_start":[0.52157,-0.02024,0.0292],"tcp_to_object_dist_end":0.01491,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":258.0,"n_steps_budget":1000.0,"object_pos_end":[0.61459,0.19093,0.22718],"object_pos_start":[0.54531,-0.02094,0.13849],"object_to_goal_dist_end":0.04201,"object_to_goal_dist_start":0.26613,"object_z_max":0.22681,"peak_contact_force":0.11052,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8066.0,"raw_peak_contact_force":0.13048,"tcp_end":[0.59589,0.18552,0.22986],"tcp_start":[0.53061,-0.02056,0.14099],"tcp_to_object_dist_end":0.01966,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":220.0,"n_steps_budget":1000.0,"object_pos_end":[0.6235,0.22313,0.20009],"object_pos_start":[0.61459,0.19093,0.22718],"object_to_goal_dist_end":0.01578,"object_to_goal_dist_start":0.04201,"object_z_max":0.22777,"peak_contact_force":0.10822,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5305.0,"raw_peak_contact_force":0.31695,"subtask_id":"place_goal","tcp_end":[0.60727,0.21735,0.20791],"tcp_start":[0.59589,0.18552,0.22986],"tcp_to_object_dist_end":0.01892,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```