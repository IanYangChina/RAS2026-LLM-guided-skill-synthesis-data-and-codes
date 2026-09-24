## Search State

- **Seed**: 5
- **Iteration**: 9 / 15

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

## Current Skill (Q=-0.518) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: descend_to_grasp
  anchor: object
  weight: 0.2
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.1
- id: approach_goal
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: place_object
  target_entity: object
  metric: goal_progress
  weight: 0.2
phases:
- id: approach_object
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_object
- id: descend_to_grasp
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
    tolerance: 0.015
    orientation:
      mode: keep_current
  subtask_id: descend_to_grasp
- id: grasp_action
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
  parameters:
    grasp_duration:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
- id: lift_object
  type: lift
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift_object
- id: approach_goal
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: retain_object
    when: during_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: approach_goal
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_object
- id: release_object
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    release_duration:
      type: scalar
      range:
      - 0.3
      - 1.5
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace
- id: retract_after_place
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp_action** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_duration: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=check_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=retain_object, when=during_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=1, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
- **retract_after_place** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.518
- **task_score** (E): 0.218
- **fitness_score**: 0.202  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.720

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.00 | 1.00 | 0.1274 |
| descend_to_grasp | 0.00 | 1.00 | 0.0471 |
| grasp_action | 1.00 | 1.00 | 0.0000 |
| lift_object | 0.00 | 1.00 | 0.1139 |
| approach_and_place | 0.00 | 1.00 | 0.0003 |
| release_object | 1.00 | 1.00 | 0.0192 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.449, 0.008, 0.186) | (0.516, 0.018, 0.030)→(0.499, 0.024, 0.023) | 0.234→0.241 | 1.00 / 5.000 | 305.803 | 1462.640 |
| descend_to_grasp | descend | 0.00 / step_budget | (0.449, 0.008, 0.186)→(0.464, 0.037, 0.165) | (0.499, 0.024, 0.023)→(0.499, 0.025, 0.023) | 0.241→0.241 | 1.00 / 5.000 | 400.695 | 968.447 |
| grasp_action | grasp | 1.00 / step_budget | (0.467, 0.042, 0.167)→(0.467, 0.042, 0.167) | (0.499, 0.025, 0.023)→(0.499, 0.025, 0.023) | 0.241→0.241 | 1.00 / 9.333 | 91036.461 | 289.232 |
| lift_object | lift | 0.00 / step_budget | (0.467, 0.042, 0.167)→(0.480, 0.015, 0.199) | (0.499, 0.025, 0.023)→(0.496, 0.040, 0.019) | 0.241→0.235 | 1.00 / 10.333 | 91213.542 | 549.465 |
| approach_and_place | approach | 0.00 / guard_failure | (0.480, 0.015, 0.199)→(0.480, 0.014, 0.199) | (0.496, 0.040, 0.019)→(0.496, 0.040, 0.019) | 0.235→0.235 | 1.00 / 10.667 | 91352.358 | 313.438 |
| release_object | release | 1.00 / step_budget | (0.480, 0.014, 0.199)→(0.480, 0.014, 0.218) | (0.496, 0.040, 0.019)→(0.496, 0.040, 0.019) | 0.235→0.235 | 1.00 / 5.000 | 112.581 | 384.936 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.278
- phase_score: 0.035
- phase_breakdown.approach_object_score: 0.151
- phase_breakdown.place_object_score: 0.000
- phase_breakdown.lift_object_score: 0.057
- phase_breakdown.descend_to_grasp_score: 0.046
- grasp_place_fitness: 0.231

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.231
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.278
- **Median Q (composite search score)**: -0.508
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.227


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.68254,"average_solve_count":63.0,"average_success_count":63.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_and_place.arc_height":0.12994,"approach_and_place.place_tolerance":0.03443,"approach_and_place.placement_z_offset":0.03188,"approach_and_place.transport_speed":0.05336,"approach_object.approach_speed":0.13886,"approach_object.approach_tolerance":0.0222,"descend_to_grasp.descend_tolerance":0.01533,"grasp_action.grasp_duration":1.24058,"lift_object.lift_height":0.16215,"lift_object.lift_speed":0.15664,"lift_object.lift_tolerance":0.02386,"release_object.release_duration":0.31115},"optimized_scores":{"best_composite_score":-0.48884,"best_fitness_score":0.23116,"best_task_score":0.27784},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":883.0,"contact_point_centroid":[0.64476,0.01093,-0.00044],"force_p95":372.85147,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1506.17266,"mean_force":228.17645,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.42577,0.00918,0.15737]},{"body_a":"world","body_b":"link6","contact_count":977.0,"contact_point_centroid":[0.63885,0.02761,-0.00024],"force_p95":466.07398,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":882.00036,"mean_force":302.42429,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.44525,0.04249,0.1978]},{"body_a":"world","body_b":"link6","contact_count":337.0,"contact_point_centroid":[0.66029,0.02702,-0.00033],"force_p95":349.70237,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":646.33614,"mean_force":257.91233,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45082,0.12757,0.14395]},{"body_a":"world","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.53604,0.00802,-0.00385],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":391.37985,"mean_force":17.78999,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.3837,0.00339,0.04701]},{"body_a":"world","body_b":"link6","contact_count":78.0,"contact_point_centroid":[0.65803,0.021,-0.00011],"force_p95":74.55933,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":338.50391,"mean_force":62.9281,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.45648,0.14816,0.14201]},{"body_a":"world","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.65724,0.02168,-0.00028],"force_p95":279.69261,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":279.70069,"mean_force":279.61996,"phase_index":4.0,"phase_name":"approach_and_place","phase_type":"approach","tcp_position_centroid":[0.456,0.14793,0.14292]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.51557,0.10146,0.21516],"force_p95":89.8056,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":265.13756,"mean_force":63.38716,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.45592,0.14878,0.14556]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.68014,0.03333,-0.00012],"force_p95":73.41076,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":231.95971,"mean_force":70.18989,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46271,0.07085,0.16072]},{"body_a":"link5","body_b":"hand","contact_count":2.0,"contact_point_centroid":[0.51587,0.1003,0.21204],"force_p95":189.65108,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":190.29432,"mean_force":183.86198,"phase_index":4.0,"phase_name":"approach_and_place","phase_type":"approach","tcp_position_centroid":[0.456,0.14793,0.14292]},{"body_a":"link5","body_b":"hand","contact_count":47.0,"contact_point_centroid":[0.516,0.09703,0.21423],"force_p95":178.32406,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":184.65895,"mean_force":99.38755,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45562,0.14536,0.14594]},{"body_a":"grasp_target","body_b":"link7","contact_count":154.0,"contact_point_centroid":[0.50477,0.01823,0.03572],"force_p95":3.94138,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.49215,"mean_force":0.77282,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39547,0.00382,0.08904]},{"body_a":"grasp_target","body_b":"hand","contact_count":136.0,"contact_point_centroid":[0.50207,0.03819,0.05258],"force_p95":2.46838,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.40743,"mean_force":0.8142,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39472,0.00375,0.08558]},{"body_a":"world","body_b":"grasp_target","contact_count":3647.0,"contact_point_centroid":[0.50094,0.04551,-0.00234],"force_p95":0.42235,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.53348,"mean_force":0.16629,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.43778,0.00891,0.16824]},{"body_a":"grasp_target","body_b":"link6","contact_count":62.0,"contact_point_centroid":[0.54214,0.02918,0.01482],"force_p95":0.7689,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.89966,"mean_force":0.45224,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38796,0.00357,0.07461]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.49392,0.04878,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.44559,0.04282,0.19757]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.49392,0.04878,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46271,0.07085,0.16072]}],"total_contact_groups":23},"final_pose_error":0.14854,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.49392,0.04878,0.01602],"final_tcp_position":[0.45615,0.14824,0.14289],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273396.45895,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49392,0.04878,0.01602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.19211,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":368.12782,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4904.0,"raw_peak_contact_force":1506.17266,"subtask_id":"approach_object","tcp_end":[0.46114,0.02144,0.19348],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18252,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49392,0.04878,0.01602],"object_pos_start":[0.49392,0.04878,0.01602],"object_to_goal_dist_end":0.19211,"object_to_goal_dist_start":0.19211,"object_z_max":0.01602,"peak_contact_force":421.16596,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4977.0,"raw_peak_contact_force":882.00036,"subtask_id":"descend_to_grasp","tcp_end":[0.4629,0.07049,0.16211],"tcp_start":[0.46114,0.02144,0.19348],"tcp_to_object_dist_end":0.15092,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.49392,0.04878,0.01602],"object_pos_start":[0.49392,0.04878,0.01602],"object_to_goal_dist_end":0.19211,"object_to_goal_dist_start":0.19211,"object_z_max":0.01602,"peak_contact_force":273004.12075,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3535.0,"raw_peak_contact_force":231.95971,"tcp_end":[0.46269,0.07084,0.1606],"tcp_start":[0.46269,0.07084,0.1606],"tcp_to_object_dist_end":0.14955,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":339.0,"n_steps_budget":600.0,"object_pos_end":[0.49392,0.04878,0.01602],"object_pos_start":[0.49392,0.04878,0.01602],"object_to_goal_dist_end":0.19211,"object_to_goal_dist_start":0.19211,"object_z_max":0.01602,"peak_contact_force":371.3165,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3171.0,"raw_peak_contact_force":646.33614,"subtask_id":"lift_object","tcp_end":[0.45597,0.14783,0.14293],"tcp_start":[0.46269,0.07084,0.1606],"tcp_to_object_dist_end":0.1654,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.49392,0.04878,0.01602],"object_pos_start":[0.49392,0.04878,0.01602],"object_to_goal_dist_end":0.19211,"object_to_goal_dist_start":0.19211,"object_z_max":0.01602,"peak_contact_force":273396.45895,"phase_name":"approach_and_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20.0,"raw_peak_contact_force":279.70069,"subtask_id":"place_object","tcp_end":[0.45615,0.14824,0.14289],"tcp_start":[0.45603,0.14803,0.14291],"tcp_to_object_dist_end":0.16557,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49392,0.04878,0.01602],"object_pos_start":[0.49392,0.04878,0.01602],"object_to_goal_dist_end":0.19211,"object_to_goal_dist_start":0.19211,"object_z_max":0.01602,"peak_contact_force":89.82771,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1299.0,"raw_peak_contact_force":338.50391,"tcp_end":[0.45568,0.1508,0.15637],"tcp_start":[0.45615,0.14824,0.14289],"tcp_to_object_dist_end":0.17768,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.42857,"average_solve_count":63.0,"average_success_count":63.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_and_place.arc_height":0.16023,"approach_and_place.place_tolerance":0.0224,"approach_and_place.placement_z_offset":0.04015,"approach_and_place.transport_speed":0.0646,"approach_object.approach_speed":0.16437,"approach_object.approach_tolerance":0.02997,"descend_to_grasp.descend_tolerance":0.01861,"grasp_action.grasp_duration":1.28234,"lift_object.lift_height":0.13181,"lift_object.lift_speed":0.12891,"lift_object.lift_tolerance":0.01895,"release_object.release_duration":0.28517},"optimized_scores":{"best_composite_score":-0.55829,"best_fitness_score":0.16171,"best_task_score":0.13764},"replay_outcomes":[{"contacts":{"omitted_contact_groups":8,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":885.0,"contact_point_centroid":[0.64545,-0.00454,-0.00043],"force_p95":359.6899,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1546.29714,"mean_force":220.8178,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.42454,-0.00585,0.15383]},{"body_a":"world","body_b":"link6","contact_count":965.0,"contact_point_centroid":[0.64438,-0.01398,-0.00024],"force_p95":438.84071,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1091.10083,"mean_force":281.01003,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.44569,-0.02104,0.19171]},{"body_a":"world","body_b":"link6","contact_count":72.0,"contact_point_centroid":[0.57444,-0.0413,-0.00017],"force_p95":103.73086,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":494.49821,"mean_force":72.22713,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.52436,-0.02127,0.28915]},{"body_a":"world","body_b":"link6","contact_count":299.0,"contact_point_centroid":[0.59204,-0.04025,-0.00021],"force_p95":326.08552,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":400.4447,"mean_force":247.53034,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51676,-0.00298,0.27345]},{"body_a":"link5","body_b":"hand","contact_count":2.0,"contact_point_centroid":[0.4626,-0.07838,0.2345],"force_p95":356.85033,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":357.30909,"mean_force":352.72153,"phase_index":4.0,"phase_name":"approach_and_place","phase_type":"approach","tcp_position_centroid":[0.52423,-0.02047,0.28875]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.4636,-0.07834,0.24084],"force_p95":191.689,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":339.72412,"mean_force":159.25458,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.52482,-0.02096,0.29606]},{"body_a":"world","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.53522,0.00067,-0.00383],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":322.16276,"mean_force":13.42345,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38388,-0.00254,0.04565]},{"body_a":"link5","body_b":"hand","contact_count":182.0,"contact_point_centroid":[0.46297,-0.07715,0.23477],"force_p95":293.33158,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":297.06444,"mean_force":261.92179,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52244,-0.01622,0.28802]},{"body_a":"link5","body_b":"hand","contact_count":62.0,"contact_point_centroid":[0.54516,0.06549,0.16367],"force_p95":193.84582,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":249.19668,"mean_force":84.54811,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46398,-0.01729,0.16058]},{"body_a":"world","body_b":"link6","contact_count":485.0,"contact_point_centroid":[0.68958,-0.05412,-9e-05],"force_p95":62.34474,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":214.07152,"mean_force":41.98095,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.47351,0.00646,0.1705]},{"body_a":"world","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.57513,-0.04136,-0.00028],"force_p95":196.1657,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":196.41635,"mean_force":193.90985,"phase_index":4.0,"phase_name":"approach_and_place","phase_type":"approach","tcp_position_centroid":[0.52423,-0.02047,0.28875]},{"body_a":"grasp_target","body_b":"link7","contact_count":360.0,"contact_point_centroid":[0.50312,-0.02121,0.04288],"force_p95":1.29102,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.87856,"mean_force":0.47799,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40265,-0.00326,0.11338]},{"body_a":"grasp_target","body_b":"hand","contact_count":270.0,"contact_point_centroid":[0.49398,-0.0294,0.05451],"force_p95":2.78348,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.61225,"mean_force":0.64468,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39928,-0.00292,0.10115]},{"body_a":"world","body_b":"grasp_target","contact_count":3183.0,"contact_point_centroid":[0.49509,-0.01673,-0.00245],"force_p95":0.27183,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.4842,"mean_force":0.16952,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.44026,-0.00587,0.1695]},{"body_a":"grasp_target","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.51897,-0.03039,0.05791],"force_p95":0.77685,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.79102,"mean_force":0.51712,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4776,0.02251,0.18983]},{"body_a":"world","body_b":"grasp_target","contact_count":1188.0,"contact_point_centroid":[0.49049,0.02065,-0.00222],"force_p95":0.33826,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65055,"mean_force":0.14232,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51546,-0.00366,0.27085]}],"total_contact_groups":24},"final_pose_error":0.21767,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.48828,0.02967,0.01602],"final_tcp_position":[0.52416,-0.02098,0.28928],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273004.12214,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49865,-0.01623,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31401,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":353.65775,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4722.0,"raw_peak_contact_force":1546.29714,"subtask_id":"approach_object","tcp_end":[0.46128,-0.01291,0.19376],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17188,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49865,-0.01623,0.02602],"object_pos_start":[0.49865,-0.01623,0.02602],"object_to_goal_dist_end":0.31401,"object_to_goal_dist_start":0.31401,"object_z_max":0.02602,"peak_contact_force":324.80319,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5027.0,"raw_peak_contact_force":1091.10083,"subtask_id":"descend_to_grasp","tcp_end":[0.46352,-0.00662,0.16351],"tcp_start":[0.46128,-0.01291,0.19376],"tcp_to_object_dist_end":0.14223,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.49865,-0.01623,0.02602],"object_pos_start":[0.49865,-0.01623,0.02602],"object_to_goal_dist_end":0.31401,"object_to_goal_dist_start":0.31401,"object_z_max":0.02602,"peak_contact_force":37.45609,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3458.0,"raw_peak_contact_force":214.07152,"tcp_end":[0.47372,0.00685,0.17059],"tcp_start":[0.47372,0.00682,0.17059],"tcp_to_object_dist_end":0.14851,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":339.0,"n_steps_budget":600.0,"object_pos_end":[0.48828,0.02967,0.01602],"object_pos_start":[0.49865,-0.01623,0.02602],"object_to_goal_dist_end":0.29747,"object_to_goal_dist_start":0.31401,"object_z_max":0.02959,"peak_contact_force":272997.14803,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3165.0,"raw_peak_contact_force":400.4447,"subtask_id":"lift_object","tcp_end":[0.52424,-0.02036,0.28864],"tcp_start":[0.47372,0.00685,0.17059],"tcp_to_object_dist_end":0.2795,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.48828,0.02967,0.01602],"object_pos_start":[0.48828,0.02967,0.01602],"object_to_goal_dist_end":0.29747,"object_to_goal_dist_start":0.29747,"object_z_max":0.01602,"peak_contact_force":357.30909,"phase_name":"approach_and_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22.0,"raw_peak_contact_force":357.30909,"subtask_id":"place_object","tcp_end":[0.52416,-0.02098,0.28928],"tcp_start":[0.52422,-0.02058,0.28886],"tcp_to_object_dist_end":0.28022,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48828,0.02967,0.01602],"object_pos_start":[0.48828,0.02967,0.01602],"object_to_goal_dist_end":0.29747,"object_to_goal_dist_start":0.29747,"object_z_max":0.01602,"peak_contact_force":187.14031,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1292.0,"raw_peak_contact_force":494.49821,"tcp_end":[0.52613,-0.02013,0.31671],"tcp_start":[0.52416,-0.02098,0.28928],"tcp_to_object_dist_end":0.30712,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.44615,"average_solve_count":65.0,"average_success_count":65.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_and_place.arc_height":0.15695,"approach_and_place.place_tolerance":0.02721,"approach_and_place.placement_z_offset":0.03631,"approach_and_place.transport_speed":0.06845,"approach_object.approach_speed":0.07971,"approach_object.approach_tolerance":0.03224,"descend_to_grasp.descend_tolerance":0.01629,"grasp_action.grasp_duration":0.9415,"lift_object.lift_height":0.22164,"lift_object.lift_speed":0.09995,"lift_object.lift_tolerance":0.03197,"release_object.release_duration":0.36734},"optimized_scores":{"best_composite_score":-0.508,"best_fitness_score":0.212,"best_task_score":0.23766},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.64295,0.00916,-0.00045],"force_p95":204.30097,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1335.45059,"mean_force":200.61713,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40635,0.00871,0.12906]},{"body_a":"world","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.53488,0.00925,-0.00317],"force_p95":264.97274,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1299.04923,"mean_force":67.11591,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38342,0.00471,0.04659]},{"body_a":"world","body_b":"link6","contact_count":975.0,"contact_point_centroid":[0.63129,0.02093,-0.00023],"force_p95":495.10392,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":932.24003,"mean_force":289.46584,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.43183,0.02426,0.19027]},{"body_a":"world","body_b":"link6","contact_count":424.0,"contact_point_centroid":[0.61812,0.06598,-0.00022],"force_p95":384.05173,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":601.61379,"mean_force":282.43238,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45457,-0.05469,0.17987]},{"body_a":"world","body_b":"link6","contact_count":542.0,"contact_point_centroid":[0.67916,0.0363,-0.00012],"force_p95":71.96504,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":421.66544,"mean_force":72.20954,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.4647,0.04721,0.16851]},{"body_a":"world","body_b":"link6","contact_count":72.0,"contact_point_centroid":[0.61354,0.07782,-0.00014],"force_p95":82.51402,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":321.80443,"mean_force":70.62593,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.45995,-0.08379,0.16527]},{"body_a":"world","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.6133,0.07706,-0.00027],"force_p95":301.01237,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":303.30507,"mean_force":280.37805,"phase_index":4.0,"phase_name":"approach_and_place","phase_type":"approach","tcp_position_centroid":[0.45969,-0.08388,0.16564]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.46205,0.02673,0.1981],"force_p95":61.16585,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":283.57383,"mean_force":50.34814,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.45943,-0.08476,0.16944]},{"body_a":"link5","body_b":"hand","contact_count":328.0,"contact_point_centroid":[0.46368,0.04125,0.19566],"force_p95":187.83133,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":275.75325,"mean_force":144.31743,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45728,-0.07242,0.17736]},{"body_a":"link5","body_b":"hand","contact_count":2.0,"contact_point_centroid":[0.46215,0.02756,0.19401],"force_p95":48.99489,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":51.57357,"mean_force":25.78679,"phase_index":4.0,"phase_name":"approach_and_place","phase_type":"approach","tcp_position_centroid":[0.45969,-0.08388,0.16564]},{"body_a":"grasp_target","body_b":"link7","contact_count":682.0,"contact_point_centroid":[0.5017,0.02441,0.0469],"force_p95":0.7971,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.82964,"mean_force":0.29657,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40268,0.00747,0.11847]},{"body_a":"grasp_target","body_b":"hand","contact_count":400.0,"contact_point_centroid":[0.49566,0.02336,0.05624],"force_p95":1.63231,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.80886,"mean_force":0.39458,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39765,0.00598,0.10241]},{"body_a":"world","body_b":"grasp_target","contact_count":2583.0,"contact_point_centroid":[0.49896,0.04309,-0.00338],"force_p95":0.36025,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.5554,"mean_force":0.23136,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.42412,0.00842,0.14567]},{"body_a":"grasp_target","body_b":"link7","contact_count":248.0,"contact_point_centroid":[0.51546,0.02156,0.05351],"force_p95":0.24218,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24516,"mean_force":0.14865,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.40322,0.01764,0.15974]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50498,0.04117,-0.00211],"force_p95":0.18749,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23084,"mean_force":0.13054,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4325,0.02457,0.1903]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.50481,0.04127,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.46471,0.04721,0.16853]}],"total_contact_groups":23},"final_pose_error":0.30689,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.50481,0.04127,0.02602],"final_tcp_position":[0.45982,-0.084,0.1658],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1335.45059,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50571,0.04054,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21548,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":195.62453,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4576.0,"raw_peak_contact_force":1335.45059,"subtask_id":"approach_object","tcp_end":[0.42388,0.01461,0.17051],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16806,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50481,0.04127,0.02602],"object_pos_start":[0.50571,0.04054,0.02602],"object_to_goal_dist_end":0.21554,"object_to_goal_dist_start":0.21548,"object_z_max":0.02603,"peak_contact_force":456.11697,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5223.0,"raw_peak_contact_force":932.24003,"subtask_id":"descend_to_grasp","tcp_end":[0.46485,0.04679,0.16998],"tcp_start":[0.42388,0.01461,0.17051],"tcp_to_object_dist_end":0.14951,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50481,0.04127,0.02602],"object_pos_start":[0.50481,0.04127,0.02602],"object_to_goal_dist_end":0.21554,"object_to_goal_dist_start":0.21554,"object_z_max":0.02602,"peak_contact_force":67.80759,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3519.0,"raw_peak_contact_force":421.66544,"tcp_end":[0.46469,0.04724,0.16841],"tcp_start":[0.46469,0.04724,0.16841],"tcp_to_object_dist_end":0.14806,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.50481,0.04127,0.02602],"object_pos_start":[0.50481,0.04127,0.02602],"object_to_goal_dist_end":0.21554,"object_to_goal_dist_start":0.21554,"object_z_max":0.02602,"peak_contact_force":272.16086,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4511.0,"raw_peak_contact_force":601.61379,"subtask_id":"lift_object","tcp_end":[0.45967,-0.08384,0.1656],"tcp_start":[0.46469,0.04724,0.16841],"tcp_to_object_dist_end":0.19281,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.50481,0.04127,0.02602],"object_pos_start":[0.50481,0.04127,0.02602],"object_to_goal_dist_end":0.21554,"object_to_goal_dist_start":0.21554,"object_z_max":0.02602,"peak_contact_force":303.30507,"phase_name":"approach_and_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20.0,"raw_peak_contact_force":303.30507,"subtask_id":"place_object","tcp_end":[0.45982,-0.084,0.1658],"tcp_start":[0.45971,-0.08392,0.16568],"tcp_to_object_dist_end":0.19301,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50481,0.04127,0.02602],"object_pos_start":[0.50481,0.04127,0.02602],"object_to_goal_dist_end":0.21554,"object_to_goal_dist_start":0.21554,"object_z_max":0.02602,"peak_contact_force":60.77422,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1291.0,"raw_peak_contact_force":321.80443,"tcp_end":[0.45912,-0.08725,0.18188],"tcp_start":[0.45982,-0.084,0.1658],"tcp_to_object_dist_end":0.20712,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```