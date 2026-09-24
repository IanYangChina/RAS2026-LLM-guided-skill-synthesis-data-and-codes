## Search State

- **Seed**: 2
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

## Current Skill (Q=-0.304) — your mutation base

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

- **Composite score**: -0.304
- **task_score** (E): 0.133
- **fitness_score**: 0.146  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.1718 |
| descend_1 | 0.00 | 1.00 | 0.0799 |
| grasp_1 | 1.00 | 1.00 | 0.0000 |
| lift_1 | 0.33 | 1.00 | 0.0713 |
| transport_1 | 0.00 | 1.00 | 0.0656 |
| place_descend_1 | 0.00 | 1.00 | 0.0039 |
| release_1 | 1.00 | 1.00 | 0.0259 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.409, -0.009, 0.156) | (0.493, -0.015, 0.030)→(0.455, -0.012, 0.016) | 0.279→0.305 | 1.00 / 5.000 | 253.487 | 1365.199 |
| descend_1 | descend | 0.00 / step_budget | (0.409, -0.009, 0.156)→(0.461, -0.021, 0.186) | (0.455, -0.012, 0.016)→(0.455, -0.012, 0.016) | 0.305→0.305 | 1.00 / 5.000 | 308.247 | 991.970 |
| grasp_1 | grasp | 1.00 / step_budget | (0.461, -0.022, 0.185)→(0.461, -0.022, 0.185) | (0.455, -0.012, 0.016)→(0.455, -0.012, 0.016) | 0.305→0.305 | 1.00 / 9.667 | 91047.447 | 498.802 |
| lift_1 | lift | 0.33 / step_budget | (0.461, -0.022, 0.185)→(0.470, -0.023, 0.240) | (0.455, -0.012, 0.016)→(0.455, -0.012, 0.016) | 0.305→0.305 | 1.00 / 8.667 | 116.159 | 460.411 |
| transport_1 | approach | 0.00 / step_budget | (0.470, -0.023, 0.240)→(0.517, 0.015, 0.265) | (0.455, -0.012, 0.016)→(0.455, -0.012, 0.016) | 0.305→0.305 | 1.00 / 9.333 | 193.123 | 482.247 |
| place_descend_1 | descend | 0.00 / step_budget | (0.517, 0.015, 0.265)→(0.517, 0.017, 0.263) | (0.455, -0.012, 0.016)→(0.455, -0.012, 0.016) | 0.305→0.305 | 1.00 / 9.000 | 243.026 | 204.385 |
| release_1 | release | 1.00 / step_budget | (0.517, 0.017, 0.263)→(0.519, 0.013, 0.287) | (0.455, -0.012, 0.016)→(0.455, -0.012, 0.016) | 0.305→0.305 | 1.00 / 4.667 | 87.846 | 136.546 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.171
- phase_score: 0.047
- phase_breakdown.reach_goal_score: 0.012
- phase_breakdown.reach_object_score: 0.134
- phase_breakdown.descend_object_score: 0.073
- phase_breakdown.place_goal_score: 0.007
- grasp_place_fitness: 0.175

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.175
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.171
- **Median Q (composite search score)**: -0.316
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.410


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":36.0,"average_failure_rate":0.31858,"average_mean_iterations":68.35398,"average_solve_count":113.0,"average_success_count":77.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset_z":0.19999,"descend_1.descend_offset_z":0.04209,"grasp_1.grasp_duration":1.06312,"lift_1.lift_offset_z":0.22813,"release_1.release_duration":1.254,"transport_1.transport_speed":0.6876},"optimized_scores":{"best_composite_score":-0.31609,"best_fitness_score":0.13391,"best_task_score":0.11973},"replay_outcomes":[{"contacts":{"omitted_contact_groups":6,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.62753,-0.00747,-0.00048],"force_p95":202.62587,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1350.95444,"mean_force":204.93765,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38437,-0.00735,0.12009]},{"body_a":"world","body_b":"link6","contact_count":992.0,"contact_point_centroid":[0.62037,-0.01628,-0.00023],"force_p95":439.2613,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":925.55315,"mean_force":271.06941,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.42173,-0.01856,0.18922]},{"body_a":"world","body_b":"link6","contact_count":547.0,"contact_point_centroid":[0.65834,-0.02502,-0.00013],"force_p95":79.42275,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":654.46557,"mean_force":73.60484,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45934,-0.02852,0.19703]},{"body_a":"link5","body_b":"hand","contact_count":294.0,"contact_point_centroid":[0.54195,-0.00155,0.22674],"force_p95":441.01982,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":541.56145,"mean_force":318.65116,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52682,0.06938,0.27175]},{"body_a":"world","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.52433,0.00049,-0.00324],"force_p95":26.43511,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":528.70226,"mean_force":26.43511,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.36893,-0.0035,0.05116]},{"body_a":"link5","body_b":"hand","contact_count":14.0,"contact_point_centroid":[0.54195,0.01722,0.20895],"force_p95":273.34288,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":277.05398,"mean_force":247.33763,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.53851,0.07597,0.28166]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.53956,0.02424,0.20027],"force_p95":184.36603,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":193.67477,"mean_force":158.40753,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.53776,0.08218,0.27397]},{"body_a":"world","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.65851,-0.02504,-9e-05],"force_p95":181.28176,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":184.72986,"mean_force":126.63106,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45925,-0.02854,0.19685]},{"body_a":"grasp_target","body_b":"hand","contact_count":37.0,"contact_point_centroid":[0.45737,-0.02412,0.03964],"force_p95":3.75899,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.1421,"mean_force":1.75721,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37962,-0.00347,0.05271]},{"body_a":"grasp_target","body_b":"link7","contact_count":30.0,"contact_point_centroid":[0.47993,-0.00754,0.01029],"force_p95":2.30567,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.82671,"mean_force":0.52174,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.3701,-0.00352,0.05627]},{"body_a":"world","body_b":"grasp_target","contact_count":3937.0,"contact_point_centroid":[0.44081,-0.02186,-0.00216],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.16254,"mean_force":0.13994,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39684,-0.0068,0.12978]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.43593,-0.02211,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.422,-0.01861,0.18938]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.43593,-0.02211,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45934,-0.02852,0.19703]},{"body_a":"world","body_b":"grasp_target","contact_count":1632.0,"contact_point_centroid":[0.43593,-0.02211,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44659,-0.02544,0.21483]},{"body_a":"world","body_b":"grasp_target","contact_count":2780.0,"contact_point_centroid":[0.43593,-0.02211,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49161,0.03755,0.24505]},{"body_a":"world","body_b":"grasp_target","contact_count":56.0,"contact_point_centroid":[0.43593,-0.02211,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.53851,0.07597,0.28166]}],"total_contact_groups":22},"final_pose_error":0.15009,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.43593,-0.02211,0.01602],"final_tcp_position":[0.538,0.08028,0.27702],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273004.12076,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43593,-0.02211,0.01602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.31838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":201.78835,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4910.0,"raw_peak_contact_force":1350.95444,"subtask_id":"reach_object","tcp_end":[0.3897,-0.01316,0.14266],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13511,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43593,-0.02211,0.01602],"object_pos_start":[0.43593,-0.02211,0.01602],"object_to_goal_dist_end":0.31838,"object_to_goal_dist_start":0.31838,"object_z_max":0.01602,"peak_contact_force":365.25597,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4992.0,"raw_peak_contact_force":925.55315,"subtask_id":"descend_object","tcp_end":[0.45951,-0.0285,0.19811],"tcp_start":[0.3897,-0.01316,0.14266],"tcp_to_object_dist_end":0.18373,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.43593,-0.02211,0.01602],"object_pos_start":[0.43593,-0.02211,0.01602],"object_to_goal_dist_end":0.31838,"object_to_goal_dist_start":0.31838,"object_z_max":0.01602,"peak_contact_force":273004.12076,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3496.0,"raw_peak_contact_force":654.46557,"tcp_end":[0.45934,-0.02855,0.19692],"tcp_start":[0.45934,-0.02854,0.19692],"tcp_to_object_dist_end":0.18252,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":408.0,"n_steps_budget":600.0,"object_pos_end":[0.43593,-0.02211,0.01602],"object_pos_start":[0.43593,-0.02211,0.01602],"object_to_goal_dist_end":0.31838,"object_to_goal_dist_start":0.31838,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3360.0,"raw_peak_contact_force":184.72986,"tcp_end":[0.43656,-0.02276,0.23422],"tcp_start":[0.45934,-0.02855,0.19692],"tcp_to_object_dist_end":0.21821,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":695.0,"n_steps_budget":1000.0,"object_pos_end":[0.43593,-0.02211,0.01602],"object_pos_start":[0.43593,-0.02211,0.01602],"object_to_goal_dist_end":0.31838,"object_to_goal_dist_start":0.31838,"object_z_max":0.01602,"peak_contact_force":265.41603,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6085.0,"raw_peak_contact_force":541.56145,"subtask_id":"reach_goal","tcp_end":[0.53881,0.07415,0.28398],"tcp_start":[0.43656,-0.02276,0.23422],"tcp_to_object_dist_end":0.30275,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":14.0,"n_steps_budget":1000.0,"object_pos_end":[0.43593,-0.02211,0.01602],"object_pos_start":[0.43593,-0.02211,0.01602],"object_to_goal_dist_end":0.31838,"object_to_goal_dist_start":0.31838,"object_z_max":0.01602,"peak_contact_force":250.87398,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":129.0,"raw_peak_contact_force":277.05398,"subtask_id":"place_goal","tcp_end":[0.538,0.08028,0.27702],"tcp_start":[0.53881,0.07415,0.28398],"tcp_to_object_dist_end":0.29837,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.43593,-0.02211,0.01602],"object_pos_start":[0.43593,-0.02211,0.01602],"object_to_goal_dist_end":0.31838,"object_to_goal_dist_start":0.31838,"object_z_max":0.01602,"peak_contact_force":182.91308,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1227.0,"raw_peak_contact_force":193.67477,"tcp_end":[0.53823,0.08264,0.29419],"tcp_start":[0.538,0.08028,0.27702],"tcp_to_object_dist_end":0.31435,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":67.0,"average_failure_rate":0.47183,"average_mean_iterations":97.8662,"average_solve_count":142.0,"average_success_count":75.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset_z":0.19196,"descend_1.descend_offset_z":0.0268,"grasp_1.grasp_duration":1.03686,"lift_1.lift_offset_z":0.05936,"release_1.release_duration":1.95169,"transport_1.transport_speed":0.51785},"optimized_scores":{"best_composite_score":-0.32151,"best_fitness_score":0.12849,"best_task_score":0.1095},"replay_outcomes":[{"contacts":{"omitted_contact_groups":10,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.62557,-0.0083,-0.00048],"force_p95":211.62749,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1338.2105,"mean_force":209.58304,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37773,-0.00825,0.11079]},{"body_a":"world","body_b":"link6","contact_count":989.0,"contact_point_centroid":[0.62202,-0.02119,-0.00023],"force_p95":465.43363,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":946.74101,"mean_force":280.21557,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.42345,-0.02274,0.18946]},{"body_a":"world","body_b":"link5","contact_count":212.0,"contact_point_centroid":[0.64603,0.10466,-0.00047],"force_p95":403.01767,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":877.25074,"mean_force":303.30442,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49188,-0.00403,0.20294]},{"body_a":"world","body_b":"link6","contact_count":543.0,"contact_point_centroid":[0.6622,-0.03432,-0.00014],"force_p95":85.45024,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":654.65586,"mean_force":73.28417,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46009,-0.03629,0.19386]},{"body_a":"world","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.52186,0.00063,-0.00305],"force_p95":25.79895,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":515.97894,"mean_force":25.79895,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.36656,-0.00337,0.05184]},{"body_a":"link5","body_b":"hand","contact_count":361.0,"contact_point_centroid":[0.52417,0.07332,0.11502],"force_p95":166.16111,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":484.3198,"mean_force":99.97637,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48573,-0.00912,0.19339]},{"body_a":"world","body_b":"link6","contact_count":112.0,"contact_point_centroid":[0.68225,-0.02471,-7e-05],"force_p95":392.72972,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":418.68525,"mean_force":213.31419,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.46608,-0.02283,0.17238]},{"body_a":"world","body_b":"link5","contact_count":2.0,"contact_point_centroid":[0.65268,0.09693,-0.00014],"force_p95":330.25306,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":335.97837,"mean_force":278.72523,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.49636,-0.0139,0.20041]},{"body_a":"world","body_b":"link6","contact_count":723.0,"contact_point_centroid":[0.6618,-0.03864,-0.0003],"force_p95":257.57252,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":263.3595,"mean_force":250.00682,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45769,-0.03326,0.18375]},{"body_a":"world","body_b":"link5","contact_count":74.0,"contact_point_centroid":[0.65285,0.09706,-8e-05],"force_p95":120.24412,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":215.83933,"mean_force":67.97715,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49622,-0.015,0.19952]},{"body_a":"link5","body_b":"hand","contact_count":198.0,"contact_point_centroid":[0.53052,0.06101,0.11909],"force_p95":80.52205,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":81.0297,"mean_force":59.96403,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49734,-0.01873,0.20575]},{"body_a":"grasp_target","body_b":"hand","contact_count":38.0,"contact_point_centroid":[0.43984,-0.0232,0.0429],"force_p95":3.56555,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.99238,"mean_force":1.54595,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.377,-0.00332,0.05376]},{"body_a":"world","body_b":"grasp_target","contact_count":3924.0,"contact_point_centroid":[0.42219,-0.02639,-0.00212],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.268,"mean_force":0.13737,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39082,-0.0076,0.1215]},{"body_a":"grasp_target","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.47016,-0.00778,0.00844],"force_p95":0.41599,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42349,"mean_force":0.21661,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.36561,-0.00337,0.05027]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.41705,-0.0264,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4238,-0.02283,0.18965]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.41705,-0.0264,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46009,-0.03629,0.19387]}],"total_contact_groups":26},"final_pose_error":0.27346,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.41705,-0.0264,0.01602],"final_tcp_position":[0.49633,-0.01423,0.20012],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1338.2105,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41705,-0.0264,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.33177,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":211.28396,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4881.0,"raw_peak_contact_force":1338.2105,"subtask_id":"reach_object","tcp_end":[0.37835,-0.01562,0.12395],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11517,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41705,-0.0264,0.01602],"object_pos_start":[0.41705,-0.0264,0.01602],"object_to_goal_dist_end":0.33177,"object_to_goal_dist_start":0.33177,"object_z_max":0.01602,"peak_contact_force":361.40003,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4989.0,"raw_peak_contact_force":946.74101,"subtask_id":"descend_object","tcp_end":[0.46026,-0.03627,0.19505],"tcp_start":[0.37835,-0.01562,0.12395],"tcp_to_object_dist_end":0.18443,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.41705,-0.0264,0.01602],"object_pos_start":[0.41705,-0.0264,0.01602],"object_to_goal_dist_end":0.33177,"object_to_goal_dist_start":0.33177,"object_z_max":0.01602,"peak_contact_force":69.35873,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3493.0,"raw_peak_contact_force":654.65586,"tcp_end":[0.46009,-0.03632,0.19376],"tcp_start":[0.46009,-0.03632,0.19376],"tcp_to_object_dist_end":0.18314,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.41705,-0.0264,0.01602],"object_pos_start":[0.41705,-0.0264,0.01602],"object_to_goal_dist_end":0.33177,"object_to_goal_dist_start":0.33177,"object_z_max":0.01602,"peak_contact_force":251.0181,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6650.0,"raw_peak_contact_force":263.3595,"tcp_end":[0.45943,-0.02993,0.17926],"tcp_start":[0.46009,-0.03632,0.19376],"tcp_to_object_dist_end":0.1687,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":361.0,"n_steps_budget":1000.0,"object_pos_end":[0.41705,-0.0264,0.01602],"object_pos_start":[0.41705,-0.0264,0.01602],"object_to_goal_dist_end":0.33177,"object_to_goal_dist_start":0.33177,"object_z_max":0.01602,"peak_contact_force":313.83054,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3716.0,"raw_peak_contact_force":877.25074,"subtask_id":"reach_goal","tcp_end":[0.49639,-0.01377,0.20053],"tcp_start":[0.45943,-0.02993,0.17926],"tcp_to_object_dist_end":0.20125,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.41705,-0.0264,0.01602],"object_pos_start":[0.41705,-0.0264,0.01602],"object_to_goal_dist_end":0.33177,"object_to_goal_dist_start":0.33177,"object_z_max":0.01602,"peak_contact_force":478.08149,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":20.0,"raw_peak_contact_force":335.97837,"subtask_id":"place_goal","tcp_end":[0.49633,-0.01423,0.20012],"tcp_start":[0.49639,-0.01377,0.20053],"tcp_to_object_dist_end":0.20081,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.41705,-0.0264,0.01602],"object_pos_start":[0.41705,-0.0264,0.01602],"object_to_goal_dist_end":0.33177,"object_to_goal_dist_start":0.33177,"object_z_max":0.01602,"peak_contact_force":80.5031,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1294.0,"raw_peak_contact_force":215.83933,"tcp_end":[0.50107,-0.02878,0.22418],"tcp_start":[0.49633,-0.01423,0.20012],"tcp_to_object_dist_end":0.22449,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":75.0,"average_failure_rate":0.57252,"average_mean_iterations":118.37405,"average_solve_count":131.0,"average_success_count":56.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset_z":0.19672,"descend_1.descend_offset_z":0.04997,"grasp_1.grasp_duration":1.40627,"lift_1.lift_offset_z":0.17492,"release_1.release_duration":0.73273,"transport_1.transport_speed":0.65997},"optimized_scores":{"best_composite_score":-0.27537,"best_fitness_score":0.17463,"best_task_score":0.17091},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":885.0,"contact_point_centroid":[0.64033,0.00246,-0.00047],"force_p95":355.52446,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1406.43274,"mean_force":221.21634,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.42448,0.00036,0.1632]},{"body_a":"world","body_b":"link6","contact_count":974.0,"contact_point_centroid":[0.63329,0.00872,-0.00024],"force_p95":500.62188,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1103.61443,"mean_force":296.25919,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.44111,0.00431,0.19844]},{"body_a":"world","body_b":"link5","contact_count":32.0,"contact_point_centroid":[0.64105,0.13754,-0.00121],"force_p95":834.64648,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":933.14446,"mean_force":519.3101,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47628,0.00264,0.1686]},{"body_a":"world","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.53643,0.0046,-0.00375],"force_p95":27.00239,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":540.04777,"mean_force":27.00239,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38141,-8e-05,0.05104]},{"body_a":"world","body_b":"link6","contact_count":74.0,"contact_point_centroid":[0.69209,0.02211,-6e-05],"force_p95":380.06106,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":430.22253,"mean_force":271.88184,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46724,0.00393,0.16166]},{"body_a":"link5","body_b":"hand","contact_count":195.0,"contact_point_centroid":[0.5231,0.08551,0.12085],"force_p95":195.98011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":310.82438,"mean_force":109.4299,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48165,-0.00124,0.18723]},{"body_a":"world","body_b":"link6","contact_count":545.0,"contact_point_centroid":[0.68263,0.01854,-0.00013],"force_p95":76.28208,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":187.2854,"mean_force":69.88308,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46442,0.00011,0.16295]},{"body_a":"link5","body_b":"hand","contact_count":1.0,"contact_point_centroid":[0.5457,0.02587,0.20457],"force_p95":27.92751,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":27.92751,"mean_force":27.92751,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51533,-0.01653,0.30724]},{"body_a":"grasp_target","body_b":"link6","contact_count":261.0,"contact_point_centroid":[0.54282,0.01667,0.03303],"force_p95":0.82368,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.55627,"mean_force":0.38814,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39863,8e-05,0.11537]},{"body_a":"grasp_target","body_b":"link7","contact_count":272.0,"contact_point_centroid":[0.53002,0.00721,0.0347],"force_p95":2.90056,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.40358,"mean_force":0.50576,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39933,8e-05,0.11189]},{"body_a":"grasp_target","body_b":"hand","contact_count":84.0,"contact_point_centroid":[0.49933,0.01407,0.04574],"force_p95":2.62145,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.30875,"mean_force":1.05249,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.3908,-2e-05,0.07771]},{"body_a":"world","body_b":"grasp_target","contact_count":3558.0,"contact_point_centroid":[0.51445,0.0108,-0.00221],"force_p95":0.26238,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.51279,"mean_force":0.15249,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43731,0.00039,0.17435]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.511,0.01352,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.44165,0.00444,0.19816]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.511,0.01352,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46442,0.00011,0.16295]},{"body_a":"world","body_b":"grasp_target","contact_count":860.0,"contact_point_centroid":[0.511,0.01352,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48151,-0.00129,0.19112]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.511,0.01352,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51533,-0.01653,0.30724]}],"total_contact_groups":23},"final_pose_error":0.2492,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.511,0.01352,0.01602],"final_tcp_position":[0.51572,-0.0163,0.31064],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1406.43274,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.511,0.01352,0.01602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.26499,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":347.38816,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5080.0,"raw_peak_contact_force":1406.43274,"subtask_id":"reach_object","tcp_end":[0.45839,0.00103,0.20192],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19361,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.511,0.01352,0.01602],"object_pos_start":[0.511,0.01352,0.01602],"object_to_goal_dist_end":0.26499,"object_to_goal_dist_start":0.26499,"object_z_max":0.01602,"peak_contact_force":198.08469,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4974.0,"raw_peak_contact_force":1103.61443,"subtask_id":"descend_object","tcp_end":[0.46442,0.00081,0.16345],"tcp_start":[0.45839,0.00103,0.20192],"tcp_to_object_dist_end":0.15513,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.511,0.01352,0.01602],"object_pos_start":[0.511,0.01352,0.01602],"object_to_goal_dist_end":0.26499,"object_to_goal_dist_start":0.26499,"object_z_max":0.01602,"peak_contact_force":68.8616,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3550.0,"raw_peak_contact_force":187.2854,"tcp_end":[0.46442,5e-05,0.16286],"tcp_start":[0.46442,6e-05,0.16286],"tcp_to_object_dist_end":0.15464,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":215.0,"n_steps_budget":600.0,"object_pos_end":[0.511,0.01352,0.01602],"object_pos_start":[0.511,0.01352,0.01602],"object_to_goal_dist_end":0.26499,"object_to_goal_dist_start":0.26499,"object_z_max":0.01602,"peak_contact_force":97.33511,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2107.0,"raw_peak_contact_force":933.14446,"tcp_end":[0.51533,-0.01653,0.30724],"tcp_start":[0.46442,5e-05,0.16286],"tcp_to_object_dist_end":0.2928,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.511,0.01352,0.01602],"object_pos_start":[0.511,0.01352,0.01602],"object_to_goal_dist_end":0.26499,"object_to_goal_dist_start":0.26499,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9.0,"raw_peak_contact_force":27.92751,"subtask_id":"reach_goal","tcp_end":[0.51554,-0.01645,0.30902],"tcp_start":[0.51533,-0.01653,0.30724],"tcp_to_object_dist_end":0.29456,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.511,0.01352,0.01602],"object_pos_start":[0.511,0.01352,0.01602],"object_to_goal_dist_end":0.26499,"object_to_goal_dist_start":0.26499,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.51572,-0.0163,0.31064],"tcp_start":[0.51554,-0.01645,0.30902],"tcp_to_object_dist_end":0.29617,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.511,0.01352,0.01602],"object_pos_start":[0.511,0.01352,0.01602],"object_to_goal_dist_end":0.26499,"object_to_goal_dist_start":0.26499,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51659,-0.0159,0.34233],"tcp_start":[0.51572,-0.0163,0.31064],"tcp_to_object_dist_end":0.32769,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```