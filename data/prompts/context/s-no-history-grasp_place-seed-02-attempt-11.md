## Search State

- **Seed**: 2
- **Iteration**: 12 / 15

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

## Current Skill (Q=0.015) — your mutation base

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

- **Composite score**: 0.015
- **task_score** (E): 0.194
- **fitness_score**: 0.470  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1157 |
| align_1 | 1.00 | 1.00 | 0.1317 |
| descend_1 | 1.00 | 1.00 | 0.0004 |
| grasp_1 | 1.00 | 1.00 | 0.0113 |
| lift_1 | 1.00 | 1.00 | 0.0758 |
| transport_1 | 1.00 | 1.00 | 0.2407 |
| place_descend_1 | 1.00 | 1.00 | 0.1208 |
| release_1 | 1.00 | 1.00 | 0.0197 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.492, -0.013, 0.192) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.138 |
| align_1 | align | 1.00 / step_budget | (0.492, -0.013, 0.192)→(0.488, -0.015, 0.060) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_1 | descend | 1.00 / force_exceeded | (0.488, -0.015, 0.060)→(0.488, -0.015, 0.060) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 93.661 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.488, -0.015, 0.060)→(0.481, -0.015, 0.051) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 36.667 | 0.139 | 0.166 |
| lift_1 | lift | 1.00 / step_budget | (0.486, -0.015, 0.110)→(0.492, -0.015, 0.185) | (0.493, -0.015, 0.026)→(0.500, -0.017, 0.091) | 0.281→0.248 | 1.00 / 15.333 | 0.129 | 0.791 |
| transport_1 | approach | 1.00 / step_budget | (0.492, -0.015, 0.185)→(0.616, 0.150, 0.290) | (0.500, -0.016, 0.093)→(0.525, 0.022, 0.016) | 0.247→0.251 | 1.00 / 8.000 | 3249.638 | 1.067 |
| place_descend_1 | descend | 1.00 / step_budget | (0.616, 0.150, 0.290)→(0.630, 0.171, 0.171) | (0.525, 0.022, 0.016)→(0.525, 0.022, 0.016) | 0.251→0.251 | 1.00 / 9.000 | 273006.621 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.630, 0.171, 0.171)→(0.624, 0.169, 0.190) | (0.525, 0.022, 0.016)→(0.525, 0.022, 0.016) | 0.251→0.251 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.239
- phase_score: 0.617
- phase_breakdown.reach_goal_score: 0.429
- phase_breakdown.reach_object_score: 0.657
- phase_breakdown.align_object_score: 0.541
- phase_breakdown.place_goal_score: 0.821
- grasp_place_fitness: 0.578

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.578
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.239
- **Median Q (composite search score)**: 0.104
- **K-run variance**: 0.0193
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.380


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.08333,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_offset_z":0.03343,"approach_1.approach_offset_z":0.19618,"descend_1.descend_force_threshold":5.1745,"grasp_1.grasp_duration":1.23227,"grasp_1.grasp_retry_offset_x":0.01824,"lift_1.lift_offset_z":0.15534,"release_1.release_duration":1.48023,"transport_1.transport_speed":0.76609},"optimized_scores":{"best_composite_score":0.1037,"best_fitness_score":0.5587,"best_task_score":0.20877},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2992.0,"contact_point_centroid":[0.52618,0.0413,-0.00233],"force_p95":0.12832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.54026,"mean_force":0.13915,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55577,0.07711,0.2542]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4887.0,"contact_point_centroid":[0.46819,-0.00131,0.10179],"force_p95":0.13724,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2981,"mean_force":0.10188,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46569,-0.01964,0.10507]},{"body_a":"world","body_b":"grasp_target","contact_count":91.0,"contact_point_centroid":[0.47517,-0.01932,-0.00122],"force_p95":0.25049,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28779,"mean_force":0.04071,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46316,-0.01967,0.05528]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5153.0,"contact_point_centroid":[0.46811,-0.0379,0.10211],"force_p95":0.13303,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28063,"mean_force":0.09712,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46575,-0.01964,0.10559]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1497.0,"contact_point_centroid":[0.48623,0.0107,0.17123],"force_p95":0.14328,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23722,"mean_force":0.10233,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48017,-0.00756,0.17526]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1521.0,"contact_point_centroid":[0.48552,-0.02649,0.1706],"force_p95":0.13674,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2111,"mean_force":0.09891,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.47954,-0.00835,0.17462]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.0201,-0.00203],"force_p95":0.1346,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16701,"mean_force":0.12549,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4652,-0.01973,0.0548]},{"body_a":"world","body_b":"grasp_target","contact_count":836.0,"contact_point_centroid":[0.47616,-0.02015,-0.00185],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12321,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48886,-0.0076,0.2684]},{"body_a":"world","body_b":"grasp_target","contact_count":3504.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47347,-0.01808,0.1448]},{"body_a":"world","body_b":"grasp_target","contact_count":16.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4717,-0.01988,0.06169]},{"body_a":"world","body_b":"grasp_target","contact_count":1280.0,"contact_point_centroid":[0.52624,0.04138,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.61587,0.14461,0.25267]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52624,0.04138,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.621,0.15405,0.19617]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2671.0,"contact_point_centroid":[0.46431,-0.00095,0.05097],"force_p95":0.09775,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10212,"mean_force":0.07612,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46411,-0.0197,0.05369]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2944.0,"contact_point_centroid":[0.46404,-0.03838,0.05073],"force_p95":0.09248,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09254,"mean_force":0.06998,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46411,-0.0197,0.05369]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2964.0,"contact_point_centroid":[0.56004,0.08152,0.26066],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01626,"mean_force":0.01049,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55977,0.08152,0.25839]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1367.0,"contact_point_centroid":[0.61626,0.14468,0.25457],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.01044,"phase_index":6.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.61592,0.14467,0.25229]}],"total_contact_groups":17},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.52624,0.04138,0.01602],"final_tcp_position":[0.62508,0.15514,0.19653],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273006.55802,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":836.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47789,-0.01627,0.23511],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20914,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":876.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3504.0,"raw_peak_contact_force":0.12263,"subtask_id":"align_object","tcp_end":[0.47182,-0.01988,0.06187],"tcp_start":[0.47789,-0.01627,0.23511],"tcp_to_object_dist_end":0.03612,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":16.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47154,-0.01988,0.06135],"tcp_start":[0.47182,-0.01988,0.06187],"tcp_to_object_dist_end":0.03564,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47609,-0.01979,0.02587],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28828,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13329,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7415.0,"raw_peak_contact_force":0.16701,"tcp_end":[0.46408,-0.0197,0.05366],"tcp_start":[0.47154,-0.01988,0.06135],"tcp_to_object_dist_end":0.03027,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":518.0,"n_steps_budget":810.0,"object_pos_end":[0.47802,-0.01943,0.13178],"object_pos_start":[0.47609,-0.01979,0.02587],"object_to_goal_dist_end":0.24255,"object_to_goal_dist_start":0.28828,"object_z_max":0.13161,"peak_contact_force":0.1352,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10131.0,"raw_peak_contact_force":0.2981,"tcp_end":[0.47161,-0.01968,0.167],"tcp_start":[0.46408,-0.0197,0.05366],"tcp_to_object_dist_end":0.0358,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52624,0.04138,0.01602],"object_pos_start":[0.47802,-0.01943,0.13178],"object_to_goal_dist_end":0.23498,"object_to_goal_dist_start":0.24255,"object_z_max":0.14672,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8974.0,"raw_peak_contact_force":1.54026,"subtask_id":"reach_goal","tcp_end":[0.60853,0.13531,0.30922],"tcp_start":[0.47161,-0.01968,0.167],"tcp_to_object_dist_end":0.31868,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":320.0,"n_steps_budget":1000.0,"object_pos_end":[0.52624,0.04138,0.01602],"object_pos_start":[0.52624,0.04138,0.01602],"object_to_goal_dist_end":0.23498,"object_to_goal_dist_start":0.23498,"object_z_max":0.01602,"peak_contact_force":273006.55802,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2647.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.62508,0.15514,0.19653],"tcp_start":[0.60853,0.13531,0.30922],"tcp_to_object_dist_end":0.23515,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52624,0.04138,0.01602],"object_pos_start":[0.52624,0.04138,0.01602],"object_to_goal_dist_end":0.23498,"object_to_goal_dist_start":0.23498,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1014.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61957,0.15359,0.21558],"tcp_start":[0.62508,0.15514,0.19653],"tcp_to_object_dist_end":0.24724,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64021,"average_solve_count":189.0,"average_success_count":189.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_offset_z":0.03004,"approach_1.approach_offset_z":0.17101,"descend_1.descend_force_threshold":6.66196,"grasp_1.grasp_duration":0.94633,"grasp_1.grasp_retry_offset_x":0.01276,"lift_1.lift_offset_z":0.21922,"release_1.release_duration":1.62532,"transport_1.transport_speed":0.46932},"optimized_scores":{"best_composite_score":-0.18132,"best_fitness_score":0.27368,"best_task_score":0.13262},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":557.0,"contact_point_centroid":[0.47014,-0.03054,-0.00368],"force_p95":0.79157,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.73628,"mean_force":0.19293,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45628,-0.02605,0.19811]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6561.0,"contact_point_centroid":[0.4504,-0.00709,0.11096],"force_p95":0.1425,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33288,"mean_force":0.09617,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44736,-0.02558,0.11315]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8988.0,"contact_point_centroid":[0.44941,-0.04386,0.11189],"force_p95":0.13096,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28054,"mean_force":0.07386,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44732,-0.02558,0.11311]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45856,-0.02629,-0.00208],"force_p95":0.14795,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17816,"mean_force":0.12899,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44791,-0.02575,0.05209]},{"body_a":"world","body_b":"grasp_target","contact_count":1180.0,"contact_point_centroid":[0.45856,-0.02632,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48073,-0.01077,0.25549]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47307,-0.03167,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1252,"mean_force":0.12265,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53555,0.07637,0.23711]},{"body_a":"world","body_b":"grasp_target","contact_count":3140.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4564,-0.02427,0.13118]},{"body_a":"world","body_b":"grasp_target","contact_count":16.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45425,-0.02598,0.05848]},{"body_a":"world","body_b":"grasp_target","contact_count":1520.0,"contact_point_centroid":[0.47307,-0.03167,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.61446,0.19058,0.18438]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.47307,-0.03167,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61835,0.20188,0.11907]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4129.0,"contact_point_centroid":[0.44736,-0.00663,0.05081],"force_p95":0.09103,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09881,"mean_force":0.0552,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44686,-0.02571,0.05105]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4952.0,"contact_point_centroid":[0.44661,-0.04466,0.05109],"force_p95":0.0735,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08036,"mean_force":0.04437,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44686,-0.02571,0.05106]},{"body_a":"left_finger","body_b":"right_finger","contact_count":264.0,"contact_point_centroid":[0.4618,-0.02657,0.23053],"force_p95":0.01521,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01647,"mean_force":0.01151,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46169,-0.02656,0.22798]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4256.0,"contact_point_centroid":[0.53593,0.0764,0.23938],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01291,"mean_force":0.01047,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53557,0.0764,0.23711]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1626.0,"contact_point_centroid":[0.6148,0.1905,0.18709],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0128,"mean_force":0.01042,"phase_index":6.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.6144,0.19049,0.18483]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.62206,0.20305,0.11806],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01273,"mean_force":0.01005,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62143,0.20303,0.11565]}],"total_contact_groups":16},"final_pose_error":0.00983,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.47307,-0.03167,0.01602],"final_tcp_position":[0.62346,0.20358,0.11966],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273007.14147,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":296.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1180.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.46128,-0.02261,0.20976],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1838,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":785.0,"n_steps_budget":960.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3140.0,"raw_peak_contact_force":0.12263,"subtask_id":"align_object","tcp_end":[0.45437,-0.02598,0.05866],"tcp_start":[0.46128,-0.02261,0.20976],"tcp_to_object_dist_end":0.03291,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":16.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45409,-0.02598,0.05817],"tcp_start":[0.45437,-0.02598,0.05866],"tcp_to_object_dist_end":0.03246,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45848,-0.02578,0.02552],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30343,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.15134,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10881.0,"raw_peak_contact_force":0.17816,"tcp_end":[0.44683,-0.0257,0.05103],"tcp_start":[0.45409,-0.02598,0.05817],"tcp_to_object_dist_end":0.02804,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":861.0,"n_steps_budget":1000.0,"object_pos_end":[0.47388,-0.03364,0.01111],"object_pos_start":[0.45848,-0.02578,0.02552],"object_to_goal_dist_end":0.30581,"object_to_goal_dist_start":0.30343,"object_z_max":0.1642,"peak_contact_force":0.12537,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16370.0,"raw_peak_contact_force":1.73628,"tcp_end":[0.46584,-0.02689,0.22695],"tcp_start":[0.46443,-0.02695,0.2275],"tcp_to_object_dist_end":0.21609,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47307,-0.03167,0.01602],"object_pos_start":[0.47304,-0.03157,0.01607],"object_to_goal_dist_end":0.30305,"object_to_goal_dist_start":0.30296,"object_z_max":0.01607,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8256.0,"raw_peak_contact_force":0.1252,"subtask_id":"reach_goal","tcp_end":[0.60781,0.17882,0.25107],"tcp_start":[0.46584,-0.02689,0.22695],"tcp_to_object_dist_end":0.34309,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":380.0,"n_steps_budget":1000.0,"object_pos_end":[0.47307,-0.03167,0.01602],"object_pos_start":[0.47307,-0.03167,0.01602],"object_to_goal_dist_end":0.30305,"object_to_goal_dist_start":0.30305,"object_z_max":0.01602,"peak_contact_force":273007.14147,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3146.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.62346,0.20358,0.11966],"tcp_start":[0.60781,0.17882,0.25107],"tcp_to_object_dist_end":0.29782,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47307,-0.03167,0.01602],"object_pos_start":[0.47307,-0.03167,0.01602],"object_to_goal_dist_end":0.30305,"object_to_goal_dist_start":0.30305,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61648,0.20117,0.13837],"tcp_start":[0.62346,0.20358,0.11966],"tcp_to_object_dist_end":0.29958,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.98462,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_offset_z":0.03505,"approach_1.approach_offset_z":0.09339,"descend_1.descend_force_threshold":5.73238,"grasp_1.grasp_duration":1.74962,"grasp_1.grasp_retry_offset_x":0.00791,"lift_1.lift_offset_z":0.14979,"release_1.release_duration":0.64012,"transport_1.transport_speed":0.31757},"optimized_scores":{"best_composite_score":0.12277,"best_fitness_score":0.57777,"best_task_score":0.23937},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3086.0,"contact_point_centroid":[0.57514,0.05696,-0.00229],"force_p95":0.15123,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.53504,"mean_force":0.14016,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.59399,0.08374,0.24901]},{"body_a":"world","body_b":"grasp_target","contact_count":102.0,"contact_point_centroid":[0.54319,0.00065,-0.00122],"force_p95":0.2572,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.339,"mean_force":0.04025,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52959,0.00087,0.05139]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8742.0,"contact_point_centroid":[0.53592,0.01942,0.09947],"force_p95":0.10414,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26969,"mean_force":0.06883,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53251,0.00085,0.09947]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8049.0,"contact_point_centroid":[0.53512,-0.01799,0.09703],"force_p95":0.13365,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25648,"mean_force":0.07653,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53235,0.00085,0.09776]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1461.0,"contact_point_centroid":[0.54881,0.02604,0.16486],"force_p95":0.13699,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24637,"mean_force":0.08033,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54226,0.00814,0.16622]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":917.0,"contact_point_centroid":[0.54793,-0.01133,0.16205],"force_p95":0.17782,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22791,"mean_force":0.11504,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54173,0.00708,0.16537]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00109,-0.00203],"force_p95":0.13213,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15261,"mean_force":0.12535,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53184,0.00091,0.05127]},{"body_a":"world","body_b":"grasp_target","contact_count":2256.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51726,0.00048,0.21448]},{"body_a":"world","body_b":"grasp_target","contact_count":1900.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.53649,0.00099,0.09057]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53888,0.00104,0.0598]},{"body_a":"world","body_b":"grasp_target","contact_count":1192.0,"contact_point_centroid":[0.5752,0.05761,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.63576,0.14477,0.25336]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5752,0.05761,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63788,0.15307,0.19726]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4403.0,"contact_point_centroid":[0.53102,-0.01829,0.05045],"force_p95":0.07233,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10694,"mean_force":0.04904,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53063,0.00089,0.04982]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4834.0,"contact_point_centroid":[0.53131,0.02003,0.05037],"force_p95":0.06841,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08461,"mean_force":0.04494,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53063,0.00089,0.04982]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3143.0,"contact_point_centroid":[0.59598,0.08608,0.25396],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01636,"mean_force":0.01054,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.59563,0.08607,0.25163]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1280.0,"contact_point_centroid":[0.63637,0.14486,0.25516],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01261,"mean_force":0.01039,"phase_index":6.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.63581,0.14485,0.2529]}],"total_contact_groups":17},"final_pose_error":0.00987,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.5752,0.05761,0.01602],"final_tcp_position":[0.64199,0.15414,0.19817],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273006.16455,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":565.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2256.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53706,0.00099,0.13026],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10449,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":475.0,"n_steps_budget":600.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1900.0,"raw_peak_contact_force":0.12263,"subtask_id":"align_object","tcp_end":[0.53888,0.00104,0.0598],"tcp_start":[0.53706,0.00099,0.13026],"tcp_to_object_dist_end":0.03422,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":118.69925,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53879,0.00104,0.0597],"tcp_start":[0.53888,0.00104,0.0598],"tcp_to_object_dist_end":0.03413,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54422,0.00095,0.02586],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25037,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13154,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11037.0,"raw_peak_contact_force":0.15261,"tcp_end":[0.5306,0.00089,0.04978],"tcp_start":[0.53879,0.00104,0.0597],"tcp_to_object_dist_end":0.02752,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":594.0,"n_steps_budget":810.0,"object_pos_end":[0.54822,0.00217,0.12966],"object_pos_start":[0.54422,0.00095,0.02586],"object_to_goal_dist_end":0.19484,"object_to_goal_dist_start":0.25037,"object_z_max":0.12952,"peak_contact_force":0.12518,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16893.0,"raw_peak_contact_force":0.339,"tcp_end":[0.53944,0.00088,0.16159],"tcp_start":[0.5306,0.00089,0.04978],"tcp_to_object_dist_end":0.03313,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5752,0.05761,0.01602],"object_pos_start":[0.54822,0.00217,0.12966],"object_to_goal_dist_end":0.21446,"object_to_goal_dist_start":0.19484,"object_z_max":0.13767,"peak_contact_force":9748.66966,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8607.0,"raw_peak_contact_force":1.53504,"subtask_id":"reach_goal","tcp_end":[0.63126,0.13668,0.30841],"tcp_start":[0.53944,0.00088,0.16159],"tcp_to_object_dist_end":0.30804,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":298.0,"n_steps_budget":1000.0,"object_pos_end":[0.5752,0.05761,0.01602],"object_pos_start":[0.5752,0.05761,0.01602],"object_to_goal_dist_end":0.21446,"object_to_goal_dist_start":0.21446,"object_z_max":0.01602,"peak_contact_force":273006.16455,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2472.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.64199,0.15414,0.19817],"tcp_start":[0.63126,0.13668,0.30841],"tcp_to_object_dist_end":0.2167,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5752,0.05761,0.01602],"object_pos_start":[0.5752,0.05761,0.01602],"object_to_goal_dist_end":0.21446,"object_to_goal_dist_start":0.21446,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63646,0.15262,0.21644],"tcp_start":[0.64199,0.15414,0.19817],"tcp_to_object_dist_end":0.23011,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```