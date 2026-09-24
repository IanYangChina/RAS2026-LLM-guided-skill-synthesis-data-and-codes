## Search State

- **Seed**: 2
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
- Frozen realised-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`
- Frozen object start: [0.4761612134249316, -0.02015088565858767, 0.03]
- Frozen task target: [0.631422574059428, 0.1591915942135097, 0.1900150788948481]
- Goal object position: (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.4761612134249316, -0.02015088565858767, 0.03)
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
  frozen_object_start: [0.4762, -0.0202, 0.03]
  frozen_task_target: [0.6314, 0.1592, 0.19]
  frozen_object_starts: {'grasp_target': [0.4761612134249316, -0.02015088565858767, 0.03]}
  frozen_targets: {'place_target': [0.631422574059428, 0.1591915942135097, 0.1900150788948481]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a

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
| `object` | offset from object initial position (0.4761612134249316, -0.02015088565858767, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.631422574059428, 0.1591915942135097, 0.1900150788948481) | final destination targets |
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

## Current Skill (Q=0.180) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.2
- id: descend_object
  anchor: object
  weight: 0.2
- id: reach_goal
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: place_goal
  weight: 0.3
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
    - 0.12
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_offset_z:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_force_threshold:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: descend_object
- id: grasp_1
  type: grasp
  control: impedance_control
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
- id: lift_1
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_offset_z:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
- id: transport_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.5
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: place_descend_1
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  subtask_id: place_goal
- id: release_1
  type: release
  control: impedance_control
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
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_offset_z: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_duration: status=consumed; consumers=duration.max_time (replace)
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_offset_z: status=consumed; consumers=target.offset.z (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **place_descend_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 0.180
- **task_score** (E): 0.228
- **fitness_score**: 0.488  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.143
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1749 |
| descend_1 | 1.00 | 1.00 | 0.0750 |
| grasp_1 | 1.00 | 1.00 | 0.0112 |
| lift_1 | 1.00 | 1.00 | 0.0798 |
| transport_1 | 0.67 | 1.00 | 0.2114 |
| place_descend_1 | 1.00 | 1.00 | 0.1083 |
| release_1 | 1.00 | 1.00 | 0.0203 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.490, -0.014, 0.131) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / force_exceeded | (0.490, -0.014, 0.131)→(0.487, -0.015, 0.056) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 81.142 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.487, -0.015, 0.056)→(0.480, -0.015, 0.047) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 33.667 | 0.132 | 0.168 |
| lift_1 | lift | 1.00 / step_budget | (0.480, -0.015, 0.047)→(0.488, -0.015, 0.126) | (0.493, -0.015, 0.026)→(0.501, -0.015, 0.091) | 0.281→0.257 | 1.00 / 20.667 | 0.073 | 0.409 |
| transport_1 | approach | 0.67 / step_budget | (0.488, -0.015, 0.126)→(0.595, 0.123, 0.241) | (0.501, -0.015, 0.091)→(0.531, 0.045, 0.019) | 0.257→0.224 | 1.00 / 8.000 | 3249.653 | 1.138 |
| place_descend_1 | descend | 1.00 / step_budget | (0.595, 0.123, 0.241)→(0.624, 0.162, 0.165) | (0.531, 0.045, 0.019)→(0.531, 0.045, 0.019) | 0.224→0.224 | 1.00 / 8.667 | 185254.361 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.624, 0.162, 0.165)→(0.618, 0.161, 0.184) | (0.531, 0.045, 0.019)→(0.531, 0.045, 0.019) | 0.224→0.224 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.282
- phase_score: 0.708
- phase_breakdown.reach_goal_score: 0.373
- phase_breakdown.reach_object_score: 0.840
- phase_breakdown.descend_object_score: 0.911
- phase_breakdown.place_goal_score: 0.819
- grasp_place_fitness: 0.621

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.621
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.282
- **Median Q (composite search score)**: 0.263
- **K-run variance**: 0.0238
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at lower bound**: approach_1.approach_offset_z
- **Final σ (mean)**: 0.265


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `dde525b5f1d1bd9dc458c18c8bb170b8849a392c0909c5e3e8e19baca2e18946`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3eaf951d4314ad541ffae42f4c615c856bb77d128e3ae1cab520a1988305ba67`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.14286,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset_z":0.10656,"descend_1.descend_force_threshold":4.29181,"grasp_1.grasp_duration":1.52596,"lift_1.lift_offset_z":0.143,"release_1.release_duration":1.66592,"transport_1.transport_speed":0.57651},"optimized_scores":{"best_composite_score":0.26339,"best_fitness_score":0.57053,"best_task_score":0.21201},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2635.0,"contact_point_centroid":[0.53042,0.04228,-0.00237],"force_p95":0.12836,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.70441,"mean_force":0.13962,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56155,0.08357,0.25608]},{"body_a":"world","body_b":"grasp_target","contact_count":132.0,"contact_point_centroid":[0.47456,-0.01887,-0.00112],"force_p95":0.27066,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39719,"mean_force":0.04362,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46276,-0.01934,0.04702]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3019.0,"contact_point_centroid":[0.49093,0.01666,0.17069],"force_p95":0.13099,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33793,"mean_force":0.07961,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48476,-0.00184,0.17106]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2775.0,"contact_point_centroid":[0.48976,-0.02189,0.16945],"force_p95":0.15046,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33186,"mean_force":0.0858,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48354,-0.00326,0.16972]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11919.0,"contact_point_centroid":[0.46758,-0.03825,0.09493],"force_p95":0.09661,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26633,"mean_force":0.05984,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46521,-0.01933,0.09326]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10924.0,"contact_point_centroid":[0.46776,-0.00034,0.0956],"force_p95":0.10338,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26626,"mean_force":0.06439,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46527,-0.01933,0.09385]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47618,-0.02005,-0.00207],"force_p95":0.14245,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19375,"mean_force":0.12814,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46497,-0.01939,0.04628]},{"body_a":"world","body_b":"grasp_target","contact_count":1848.0,"contact_point_centroid":[0.47616,-0.02015,-0.00192],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48673,-0.00888,0.22339]},{"body_a":"world","body_b":"grasp_target","contact_count":2024.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47151,-0.01886,0.09728]},{"body_a":"world","body_b":"grasp_target","contact_count":1276.0,"contact_point_centroid":[0.53044,0.04231,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.61567,0.14442,0.25164]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53044,0.04231,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62094,0.15401,0.19598]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4910.0,"contact_point_centroid":[0.46315,-7e-05,0.0489],"force_p95":0.06819,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0999,"mean_force":0.04438,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46387,-0.01937,0.04517]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5685.0,"contact_point_centroid":[0.46345,-0.03859,0.04782],"force_p95":0.06346,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07776,"mean_force":0.03929,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46387,-0.01937,0.04517]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2568.0,"contact_point_centroid":[0.56568,0.08787,0.26272],"force_p95":0.01124,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01617,"mean_force":0.01057,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56546,0.08787,0.26041]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1368.0,"contact_point_centroid":[0.61597,0.14438,0.25422],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.0104,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.61563,0.14437,0.25194]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.62366,0.15479,0.19444],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01095,"mean_force":0.01001,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62338,0.15478,0.1924]}],"total_contact_groups":16},"final_pose_error":0.00988,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.53044,0.04231,0.01602],"final_tcp_position":[0.62503,0.15509,0.19632],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":9748.81529,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":463.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1848.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47471,-0.01824,0.14626],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12026,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":506.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2024.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_object","tcp_end":[0.47135,-0.01954,0.05277],"tcp_start":[0.47471,-0.01824,0.14626],"tcp_to_object_dist_end":0.02719,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4761,-0.01952,0.02574],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28819,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13962,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12395.0,"raw_peak_contact_force":0.19375,"tcp_end":[0.46384,-0.01937,0.04514],"tcp_start":[0.47135,-0.01954,0.05277],"tcp_to_object_dist_end":0.02295,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.48392,-0.01962,0.13112],"object_pos_start":[0.4761,-0.01952,0.02574],"object_to_goal_dist_end":0.23917,"object_to_goal_dist_start":0.28819,"object_z_max":0.13101,"peak_contact_force":0.09746,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22975.0,"raw_peak_contact_force":0.39719,"tcp_end":[0.4717,-0.01941,0.15712],"tcp_start":[0.46384,-0.01937,0.04514],"tcp_to_object_dist_end":0.02872,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53044,0.04231,0.01602],"object_pos_start":[0.48392,-0.01962,0.13112],"object_to_goal_dist_end":0.23267,"object_to_goal_dist_start":0.23917,"object_z_max":0.15896,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10997.0,"raw_peak_contact_force":1.70441,"subtask_id":"reach_goal","tcp_end":[0.60822,0.13497,0.30756],"tcp_start":[0.4717,-0.01941,0.15712],"tcp_to_object_dist_end":0.31564,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":319.0,"n_steps_budget":1000.0,"object_pos_end":[0.53044,0.04231,0.01602],"object_pos_start":[0.53044,0.04231,0.01602],"object_to_goal_dist_end":0.23267,"object_to_goal_dist_start":0.23267,"object_z_max":0.01602,"peak_contact_force":9748.81529,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2644.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.62503,0.15509,0.19632],"tcp_start":[0.60822,0.13497,0.30756],"tcp_to_object_dist_end":0.23276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53044,0.04231,0.01602],"object_pos_start":[0.53044,0.04231,0.01602],"object_to_goal_dist_end":0.23267,"object_to_goal_dist_start":0.23267,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61951,0.15355,0.21538],"tcp_start":[0.62503,0.15509,0.19632],"tcp_to_object_dist_end":0.24506,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `92fc0f2bbc35407e7976a239cbab7bb266e8a517486aa3be6bd6666f4c63f38d`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.14615,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset_z":0.11865,"descend_1.descend_force_threshold":5.93889,"grasp_1.grasp_duration":1.06468,"lift_1.lift_offset_z":0.10553,"release_1.release_duration":1.38146,"transport_1.transport_speed":0.38546},"optimized_scores":{"best_composite_score":0.31391,"best_fitness_score":0.62105,"best_task_score":0.28201},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2160.0,"contact_point_centroid":[0.51618,0.08981,-0.00251],"force_p95":0.24739,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.58837,"mean_force":0.15351,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56185,0.12112,0.204]},{"body_a":"world","body_b":"grasp_target","contact_count":130.0,"contact_point_centroid":[0.45659,-0.02528,-0.00109],"force_p95":0.56888,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70791,"mean_force":0.0734,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44562,-0.0257,0.02349]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3509.0,"contact_point_centroid":[0.47569,-0.01641,0.1324],"force_p95":0.17937,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37421,"mean_force":0.09252,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.47187,0.00206,0.13355]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3797.0,"contact_point_centroid":[0.47797,0.02272,0.13374],"force_p95":0.17791,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34721,"mean_force":0.09553,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.47361,0.00449,0.13489]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10455.0,"contact_point_centroid":[0.44992,-0.00666,0.0691],"force_p95":0.10171,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27503,"mean_force":0.06277,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4481,-0.02559,0.06725]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10868.0,"contact_point_centroid":[0.44978,-0.04452,0.06734],"force_p95":0.10177,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26889,"mean_force":0.06113,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44795,-0.02559,0.06583]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45856,-0.02615,-0.00204],"force_p95":0.13701,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18848,"mean_force":0.12662,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44779,-0.02579,0.0227]},{"body_a":"world","body_b":"grasp_target","contact_count":1736.0,"contact_point_centroid":[0.45856,-0.02632,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47919,-0.0115,0.22944]},{"body_a":"world","body_b":"grasp_target","contact_count":2856.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45504,-0.02481,0.09059]},{"body_a":"world","body_b":"grasp_target","contact_count":1448.0,"contact_point_centroid":[0.51709,0.09138,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.61217,0.18916,0.1766]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51709,0.09138,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61779,0.20149,0.11829]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4818.0,"contact_point_centroid":[0.44672,-0.00654,0.02406],"force_p95":0.06756,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09194,"mean_force":0.04484,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44669,-0.02575,0.02167]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5162.0,"contact_point_centroid":[0.44657,-0.04498,0.02356],"force_p95":0.06632,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08427,"mean_force":0.04303,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4467,-0.02575,0.02167]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2259.0,"contact_point_centroid":[0.56359,0.12304,0.20737],"force_p95":0.01163,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01639,"mean_force":0.01056,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56331,0.12304,0.20514]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1557.0,"contact_point_centroid":[0.61237,0.18913,0.17909],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01265,"mean_force":0.01037,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.61214,0.18911,0.17677]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.62114,0.20266,0.11677],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01103,"mean_force":0.01003,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62089,0.20265,0.11488]}],"total_contact_groups":16},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.51709,0.09138,0.01602],"final_tcp_position":[0.62289,0.20317,0.1188],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273007.23411,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":435.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1736.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45908,-0.02368,0.15827],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13228,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":714.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2856.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_object","tcp_end":[0.45413,-0.02601,0.02866],"tcp_start":[0.45908,-0.02368,0.15827],"tcp_to_object_dist_end":0.00517,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45842,-0.02574,0.02583],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30334,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13462,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11780.0,"raw_peak_contact_force":0.18848,"tcp_end":[0.44667,-0.02574,0.02164],"tcp_start":[0.45413,-0.02601,0.02866],"tcp_to_object_dist_end":0.01248,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.47348,-0.02551,0.1151],"object_pos_start":[0.45842,-0.02574,0.02583],"object_to_goal_dist_end":0.28137,"object_to_goal_dist_start":0.30334,"object_z_max":0.115,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21453.0,"raw_peak_contact_force":0.70791,"tcp_end":[0.45382,-0.02557,0.1204],"tcp_start":[0.44667,-0.02574,0.02164],"tcp_to_object_dist_end":0.02037,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51709,0.09138,0.01602],"object_pos_start":[0.47348,-0.02551,0.1151],"object_to_goal_dist_end":0.18987,"object_to_goal_dist_start":0.28137,"object_z_max":0.13346,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11725.0,"raw_peak_contact_force":1.58837,"subtask_id":"reach_goal","tcp_end":[0.60401,0.17656,0.23676],"tcp_start":[0.45382,-0.02557,0.1204],"tcp_to_object_dist_end":0.25206,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":362.0,"n_steps_budget":1000.0,"object_pos_end":[0.51709,0.09138,0.01602],"object_pos_start":[0.51709,0.09138,0.01602],"object_to_goal_dist_end":0.18987,"object_to_goal_dist_start":0.18987,"object_z_max":0.01602,"peak_contact_force":273007.23411,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3005.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.62289,0.20317,0.1188],"tcp_start":[0.60401,0.17656,0.23676],"tcp_to_object_dist_end":0.18508,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51709,0.09138,0.01602],"object_pos_start":[0.51709,0.09138,0.01602],"object_to_goal_dist_end":0.18987,"object_to_goal_dist_start":0.18987,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61591,0.20078,0.1376],"tcp_start":[0.62289,0.20317,0.1188],"tcp_to_object_dist_end":0.19109,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3b2449a94ded39f3d450008c4da002b4ddf87103ab7d1b86900d116c316ff53`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68182,"average_solve_count":110.0,"average_success_count":110.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset_z":0.05,"descend_1.descend_force_threshold":7.07946,"grasp_1.grasp_duration":0.82956,"lift_1.lift_offset_z":0.08499,"release_1.release_duration":1.79021,"transport_1.transport_speed":0.12526},"optimized_scores":{"best_composite_score":-0.03586,"best_fitness_score":0.27128,"best_task_score":0.18872},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2780.0,"contact_point_centroid":[0.54431,0.00113,-0.00195],"force_p95":0.12911,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51744,0.00049,0.19253]},{"body_a":"world","body_b":"grasp_target","contact_count":28.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53702,0.00099,0.08642]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52993,0.00087,0.07697]},{"body_a":"world","body_b":"grasp_target","contact_count":1772.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53265,0.00093,0.08835]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5548,0.02994,0.14005]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.5993,0.09623,0.1768]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61928,0.12838,0.17987]},{"body_a":"left_finger","body_b":"right_finger","contact_count":337.0,"contact_point_centroid":[0.52911,0.00085,0.0779],"force_p95":0.01431,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01566,"mean_force":0.01123,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52875,0.00085,0.07549]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4255.0,"contact_point_centroid":[0.5551,0.02991,0.14229],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0129,"mean_force":0.01048,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55478,0.02991,0.14001]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1884.0,"contact_point_centroid":[0.53293,0.00093,0.09079],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.01048,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53266,0.00093,0.08838]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4253.0,"contact_point_centroid":[0.59969,0.09617,0.17905],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.01048,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.59925,0.09616,0.17679]},{"body_a":"left_finger","body_b":"right_finger","contact_count":218.0,"contact_point_centroid":[0.62256,0.12912,0.17839],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.011,"mean_force":0.01019,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62203,0.12911,0.17642]}],"total_contact_groups":12},"final_pose_error":0.03951,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.54431,0.00113,0.02602],"final_tcp_position":[0.62335,0.1292,0.17937],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273007.03394,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":696.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2780.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.5373,0.00099,0.08712],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0615,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":28.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_object","tcp_end":[0.53668,0.00098,0.08551],"tcp_start":[0.5373,0.00099,0.08712],"tcp_to_object_dist_end":0.05998,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2137.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52875,0.00085,0.07549],"tcp_start":[0.53668,0.00098,0.08551],"tcp_to_object_dist_end":0.05186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":443.0,"n_steps_budget":600.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3656.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53855,0.00103,0.10197],"tcp_start":[0.52875,0.00085,0.07549],"tcp_to_object_dist_end":0.07617,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":9748.71393,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8255.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.57349,0.05649,0.17986],"tcp_start":[0.53855,0.00103,0.10197],"tcp_to_object_dist_end":0.16608,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":273007.03394,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8253.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.62335,0.1292,0.17937],"tcp_start":[0.57349,0.05649,0.17986],"tcp_to_object_dist_end":0.21486,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61769,0.12796,0.19932],"tcp_start":[0.62335,0.1292,0.17937],"tcp_to_object_dist_end":0.22694,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```