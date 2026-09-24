## Search State

- **Seed**: 9
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → grasp → lift → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | impedance_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | force_exceeded | time_limit | 7 | 0.3008 | 0.25 | ✅ accepted |
| 0 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6 | -0.1649 | 0.13 | ✅ accepted |

**Proposal policy**: task_score is 0.25 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`
- Frozen object start: [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5, 0.0, 0.3)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5370249203970084, -0.021318279091244466, 0.03)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5370249203970084, -0.021318279091244466, 0.03]
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
  frozen_object_start: [0.537, -0.0213, 0.03]
  frozen_task_target: [0.6103, 0.2278, 0.2074]
  frozen_object_starts: {'grasp_target': [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]}
  frozen_targets: {'place_target': [0.5, 0.0, 0.3]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8

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
| `object` | offset from object initial position (0.6103148150051562, 0.2277534082920179, 0.2074111944405348) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
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

## Current Skill (Q=0.301) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: transport_goal
  target_entity: object
  metric: goal_progress
  weight: 0.8
phases:
- id: approach_above
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
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
  subtask_id: pre_grasp
- id: descend_grasp
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
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
  subtask_id: pre_grasp
- id: grasp_object
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  guards:
  - id: bilateral_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
  subtask_id: pre_grasp
- id: lift_and_transport
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.2
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_goal
- id: place_descend
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    force_threshold:
      type: scalar
      range:
      - 2.0
      - 15.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_goal
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
    orientation:
      mode: keep_current
  parameters:
    max_time:
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
- **approach_above** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=bilateral_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **lift_and_transport** (`lift`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.2], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **place_descend** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - max_time: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 0.301
- **task_score** (E): 0.254
- **fitness_score**: 0.604  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.470

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1203 |
| descend_grasp | 1.00 | 1.00 | 0.1468 |
| grasp_object | 1.00 | 1.00 | 0.0119 |
| lift_and_transport | 0.00 | 1.00 | 0.1420 |
| place_descend | 1.00 | 1.00 | 0.0004 |
| release_object | 1.00 | 1.00 | 0.0243 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, -0.015, 0.187) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.511, -0.015, 0.187)→(0.510, -0.017, 0.040) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.510, -0.017, 0.040)→(0.502, -0.016, 0.032) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 42.000 | 0.135 | 0.175 |
| lift_and_transport | lift | 0.00 / step_budget | (0.502, -0.016, 0.032)→(0.546, 0.057, 0.142) | (0.515, -0.016, 0.026)→(0.557, 0.056, 0.117) | 0.270→0.154 | 1.00 / 12.000 | 4.609 | 0.522 |
| place_descend | descend | 1.00 / force_exceeded | (0.546, 0.057, 0.142)→(0.546, 0.057, 0.142) | (0.557, 0.056, 0.117)→(0.557, 0.056, 0.117) | 0.154→0.154 | 1.00 / 11.333 | 59239.110 | 0.148 |
| release_object | release | 1.00 / step_budget | (0.546, 0.057, 0.142)→(0.540, 0.056, 0.166) | (0.557, 0.056, 0.117)→(0.552, 0.052, 0.016) | 0.154→0.212 | 1.00 / 4.000 | 0.125 | 1.372 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.349
- phase_score: 0.029
- phase_breakdown.pre_grasp_score: 0.136
- phase_breakdown.transport_goal_score: 0.003
- grasp_place_fitness: 0.654

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.654
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.349
- **Median Q (composite search score)**: 0.293
- **K-run variance**: 0.0015
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.349


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `425c48e82220fc6e1b680086671cf7dd2586733ee271dec2149f96a25d69d0c6`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `58e88c03db0a62276863b22a53636bc89fead3e4bc7f4d35fd72d2282ace32bf`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.61031,0.22775,0.20741]},{"name":"goal","value":[0.53702,-0.02132,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51938,"average_solve_count":129.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.0563,"descend_grasp.speed":0.07603,"lift_and_transport.lift_height":0.19624,"lift_and_transport.speed":0.05243,"place_descend.force_threshold":14.29888,"place_descend.speed":0.03024,"release_object.max_time":1.12905},"optimized_scores":{"best_composite_score":0.25853,"best_fitness_score":0.56186,"best_task_score":0.17025},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":297.0,"contact_point_centroid":[0.54412,0.05422,-0.00462],"force_p95":1.00342,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.39137,"mean_force":0.26144,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.53757,0.0499,0.14358]},{"body_a":"world","body_b":"grasp_target","contact_count":246.0,"contact_point_centroid":[0.53518,-0.01715,-0.00119],"force_p95":0.28822,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57597,"mean_force":0.1835,"phase_index":3.0,"phase_name":"lift_and_transport","phase_type":"lift","tcp_position_centroid":[0.52179,-0.01825,0.03215]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":559.0,"contact_point_centroid":[0.54588,0.03246,0.12386],"force_p95":0.14075,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.45546,"mean_force":0.099,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5418,0.05041,0.12839]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13495.0,"contact_point_centroid":[0.53295,0.03016,0.07448],"force_p95":0.12422,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29073,"mean_force":0.07375,"phase_index":3.0,"phase_name":"lift_and_transport","phase_type":"lift","tcp_position_centroid":[0.52992,0.01137,0.07345]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14885.0,"contact_point_centroid":[0.53264,-0.00789,0.07326],"force_p95":0.11956,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26923,"mean_force":0.06975,"phase_index":3.0,"phase_name":"lift_and_transport","phase_type":"lift","tcp_position_centroid":[0.52973,0.01079,0.07261]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":468.0,"contact_point_centroid":[0.54559,0.06861,0.12391],"force_p95":0.21222,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26696,"mean_force":0.10523,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5419,0.05042,0.12852]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":54.0,"contact_point_centroid":[0.54788,0.03203,0.12708],"force_p95":0.13856,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19306,"mean_force":0.10141,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.54375,0.05024,0.13123]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02115,-0.00205],"force_p95":0.13867,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17953,"mean_force":0.12701,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5243,-0.02079,0.03202]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.54721,0.06838,0.12682],"force_p95":0.14945,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.175,"mean_force":0.095,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.54375,0.05024,0.13123]},{"body_a":"world","body_b":"grasp_target","contact_count":1716.0,"contact_point_centroid":[0.53702,-0.02132,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51349,-0.00931,0.24261]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4100.0,"contact_point_centroid":[0.52379,-0.00157,0.0334],"force_p95":0.07729,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12266,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52308,-0.02077,0.03063]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52926,-0.02014,0.09767]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4907.0,"contact_point_centroid":[0.52384,-0.03986,0.03248],"force_p95":0.06954,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09196,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52308,-0.02077,0.03063]}],"total_contact_groups":13},"final_pose_error":0.20419,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.54406,0.05538,0.01656],"final_tcp_position":[0.5437,0.05044,0.13113],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":9760.30694,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":430.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1716.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.52972,-0.01905,0.1863],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16047,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"pre_grasp","tcp_end":[0.53128,-0.02093,0.04007],"tcp_start":[0.52972,-0.01905,0.1863],"tcp_to_object_dist_end":0.01518,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5369,-0.02068,0.02581],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31637,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13535,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10807.0,"raw_peak_contact_force":0.17953,"subtask_id":"pre_grasp","tcp_end":[0.52305,-0.02077,0.03059],"tcp_start":[0.53128,-0.02093,0.04007],"tcp_to_object_dist_end":0.01465,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55453,0.05008,0.11005],"object_pos_start":[0.5369,-0.02068,0.02581],"object_to_goal_dist_end":0.21015,"object_to_goal_dist_start":0.31637,"object_z_max":0.10995,"peak_contact_force":0.1357,"phase_name":"lift_and_transport","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28626.0,"raw_peak_contact_force":0.57597,"subtask_id":"transport_goal","tcp_end":[0.54371,0.0501,0.13118],"tcp_start":[0.52305,-0.02077,0.03059],"tcp_to_object_dist_end":0.02375,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.55453,0.05044,0.10977],"object_pos_start":[0.55453,0.05008,0.11005],"object_to_goal_dist_end":0.20997,"object_to_goal_dist_start":0.21015,"object_z_max":0.11007,"peak_contact_force":9760.30694,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":114.0,"raw_peak_contact_force":0.19306,"subtask_id":"transport_goal","tcp_end":[0.5437,0.05044,0.13113],"tcp_start":[0.54371,0.0501,0.13118],"tcp_to_object_dist_end":0.02395,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54406,0.05538,0.01656],"object_pos_start":[0.55453,0.05044,0.10977],"object_to_goal_dist_end":0.26557,"object_to_goal_dist_start":0.20997,"object_z_max":0.10977,"peak_contact_force":0.12535,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1324.0,"raw_peak_contact_force":1.39137,"tcp_end":[0.53744,0.04989,0.15476],"tcp_start":[0.5437,0.05044,0.13113],"tcp_to_object_dist_end":0.13848,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1e57d18e69439f9d4839513252d085a45363faa5c1c2b52093c9c8149b88bb68`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.63284,0.16493,0.17692]},{"name":"goal","value":[0.5456,-0.02923,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50394,"average_solve_count":127.0,"average_success_count":127.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.04981,"descend_grasp.speed":0.08699,"lift_and_transport.lift_height":0.2217,"lift_and_transport.speed":0.08704,"place_descend.force_threshold":3.42366,"place_descend.speed":0.03778,"release_object.max_time":0.69411},"optimized_scores":{"best_composite_score":0.29292,"best_fitness_score":0.59626,"best_task_score":0.24327},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":526.0,"contact_point_centroid":[0.57233,0.03994,-0.0037],"force_p95":0.93045,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.38263,"mean_force":0.21252,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55681,0.03789,0.15845]},{"body_a":"world","body_b":"grasp_target","contact_count":224.0,"contact_point_centroid":[0.54456,-0.02474,-0.0012],"force_p95":0.28163,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52874,"mean_force":0.16601,"phase_index":3.0,"phase_name":"lift_and_transport","phase_type":"lift","tcp_position_centroid":[0.53028,-0.02627,0.03493]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13380.0,"contact_point_centroid":[0.54522,-0.01876,0.08153],"force_p95":0.12553,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27756,"mean_force":0.0752,"phase_index":3.0,"phase_name":"lift_and_transport","phase_type":"lift","tcp_position_centroid":[0.54173,-0.00014,0.08084]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12062.0,"contact_point_centroid":[0.54534,0.01854,0.08188],"force_p95":0.13209,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27583,"mean_force":0.07969,"phase_index":3.0,"phase_name":"lift_and_transport","phase_type":"lift","tcp_position_centroid":[0.54168,-0.0002,0.0807]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54562,-0.02903,-0.00208],"force_p95":0.14576,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20569,"mean_force":0.12891,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53251,-0.02842,0.0346]},{"body_a":"world","body_b":"grasp_target","contact_count":1856.0,"contact_point_centroid":[0.5456,-0.02923,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51744,-0.01293,0.24175]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4089.0,"contact_point_centroid":[0.53213,-0.00917,0.03593],"force_p95":0.07843,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13381,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53128,-0.02838,0.03316]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53749,-0.02768,0.09745]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4939.0,"contact_point_centroid":[0.53215,-0.04749,0.035],"force_p95":0.07089,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08285,"mean_force":0.04469,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53128,-0.02838,0.03317]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1.0,"contact_point_centroid":[0.57031,0.02596,0.14596],"force_p95":0.05724,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.05724,"mean_force":0.05724,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.56225,0.03826,0.15284]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2.0,"contact_point_centroid":[0.56654,0.02562,0.14614],"force_p95":0.0,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.56218,0.0382,0.15275]}],"total_contact_groups":11},"final_pose_error":0.147,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.57234,0.04082,0.016],"final_tcp_position":[0.56225,0.03826,0.15284],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":13.4644,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":465.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1856.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53765,-0.02631,0.1853],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1595,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"pre_grasp","tcp_end":[0.53958,-0.02865,0.04295],"tcp_start":[0.53765,-0.02631,0.1853],"tcp_to_object_dist_end":0.01797,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5455,-0.02837,0.02572],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26049,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14118,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10828.0,"raw_peak_contact_force":0.20569,"subtask_id":"pre_grasp","tcp_end":[0.53125,-0.02838,0.03313],"tcp_start":[0.53958,-0.02865,0.04295],"tcp_to_object_dist_end":0.01605,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5716,0.03475,0.12093],"object_pos_start":[0.5455,-0.02837,0.02572],"object_to_goal_dist_end":0.15437,"object_to_goal_dist_start":0.26049,"object_z_max":0.1266,"peak_contact_force":13.4644,"phase_name":"lift_and_transport","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25666.0,"raw_peak_contact_force":0.52874,"subtask_id":"transport_goal","tcp_end":[0.56218,0.0382,0.15275],"tcp_start":[0.53125,-0.02838,0.03313],"tcp_to_object_dist_end":0.03337,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.57166,0.03468,0.12037],"object_pos_start":[0.5716,0.03475,0.12093],"object_to_goal_dist_end":0.15462,"object_to_goal_dist_start":0.15437,"object_z_max":0.12093,"peak_contact_force":5.29429,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2.0,"raw_peak_contact_force":0.0,"subtask_id":"transport_goal","tcp_end":[0.56225,0.03826,0.15284],"tcp_start":[0.56218,0.0382,0.15275],"tcp_to_object_dist_end":0.03399,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57234,0.04082,0.016],"object_pos_start":[0.57166,0.03468,0.12037],"object_to_goal_dist_end":0.21204,"object_to_goal_dist_start":0.15462,"object_z_max":0.12037,"peak_contact_force":0.12379,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":527.0,"raw_peak_contact_force":1.38263,"tcp_end":[0.55633,0.03786,0.17596],"tcp_start":[0.56225,0.03826,0.15284],"tcp_to_object_dist_end":0.16079,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `5836f8a66456087ed82e2e1accc6472c2a7681a19bf8e3d54637158aadaafc47`; realized-scene SHA-256: `776f3cbcac69f75f44cb26f0b1a492bbf1ced59f3c5fca79400c3f557c2ce565`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.61015,0.15287,0.12219]},{"name":"goal","value":[0.46286,-7e-05,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61015,0.15287,0.12219]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.46286,-7e-05,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.01596,"average_solve_count":188.0,"average_success_count":188.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.08288,"descend_grasp.speed":0.0105,"lift_and_transport.lift_height":0.1284,"lift_and_transport.speed":0.09928,"place_descend.force_threshold":9.63271,"place_descend.speed":0.02844,"release_object.max_time":0.98302},"optimized_scores":{"best_composite_score":0.35106,"best_fitness_score":0.65439,"best_task_score":0.3486},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":479.0,"contact_point_centroid":[0.53988,0.05966,-0.00361],"force_p95":0.8255,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.34254,"mean_force":0.20992,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.52727,0.08111,0.14989]},{"body_a":"world","body_b":"grasp_target","contact_count":215.0,"contact_point_centroid":[0.46655,0.00314,-0.00115],"force_p95":0.33509,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46056,"mean_force":0.21225,"phase_index":3.0,"phase_name":"lift_and_transport","phase_type":"lift","tcp_position_centroid":[0.45221,0.00226,0.03294]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14969.0,"contact_point_centroid":[0.48625,0.0158,0.07739],"force_p95":0.12381,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25704,"mean_force":0.0693,"phase_index":3.0,"phase_name":"lift_and_transport","phase_type":"lift","tcp_position_centroid":[0.48367,0.03453,0.0765]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13540.0,"contact_point_centroid":[0.4875,0.05457,0.07942],"force_p95":0.12922,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25191,"mean_force":0.07389,"phase_index":3.0,"phase_name":"lift_and_transport","phase_type":"lift","tcp_position_centroid":[0.48491,0.03572,0.07818]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":56.0,"contact_point_centroid":[0.53679,0.09982,0.13795],"force_p95":0.20663,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24996,"mean_force":0.13874,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.53285,0.08175,0.1429]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":64.0,"contact_point_centroid":[0.53661,0.06381,0.13801],"force_p95":0.14775,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24484,"mean_force":0.10456,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.53285,0.08175,0.1429]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":189.0,"contact_point_centroid":[0.53637,0.06553,0.13612],"force_p95":0.17137,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19708,"mean_force":0.08201,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.53211,0.08196,0.14129]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":69.0,"contact_point_centroid":[0.53841,0.09986,0.13629],"force_p95":0.1731,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19441,"mean_force":0.12409,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.53262,0.08201,0.14205]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46284,-3e-05,-0.00201],"force_p95":0.128,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14002,"mean_force":0.12427,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45244,-0.00019,0.03197]},{"body_a":"world","body_b":"grasp_target","contact_count":1356.0,"contact_point_centroid":[0.46286,-7e-05,-0.0019],"force_p95":0.13561,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48191,-4e-05,0.24542]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.45983,-9e-05,0.11036]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4389.0,"contact_point_centroid":[0.45112,0.0191,0.03294],"force_p95":0.07395,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09379,"mean_force":0.04933,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45137,-0.0002,0.03094]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5332.0,"contact_point_centroid":[0.45068,-0.01928,0.0324],"force_p95":0.06283,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08639,"mean_force":0.0409,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45137,-0.0002,0.03094]}],"total_contact_groups":13},"final_pose_error":0.10678,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.53975,0.05926,0.01604],"final_tcp_position":[0.53295,0.08197,0.14261],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":340.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1356.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.46427,-7e-05,0.18975],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"pre_grasp","tcp_end":[0.45864,-0.00012,0.03796],"tcp_start":[0.46427,-7e-05,0.18975],"tcp_to_object_dist_end":0.01267,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46274,-0.0,0.02592],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23317,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12815,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11521.0,"raw_peak_contact_force":0.14002,"subtask_id":"pre_grasp","tcp_end":[0.45134,-0.0002,0.03091],"tcp_start":[0.45864,-0.00012,0.03796],"tcp_to_object_dist_end":0.01245,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54407,0.08173,0.12108],"object_pos_start":[0.46274,-0.0,0.02592],"object_to_goal_dist_end":0.0971,"object_to_goal_dist_start":0.23317,"object_z_max":0.12099,"peak_contact_force":0.22642,"phase_name":"lift_and_transport","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28724.0,"raw_peak_contact_force":0.46056,"subtask_id":"transport_goal","tcp_end":[0.53269,0.08155,0.14289],"tcp_start":[0.45134,-0.0002,0.03091],"tcp_to_object_dist_end":0.0246,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":8.0,"n_steps_budget":1000.0,"object_pos_end":[0.54399,0.08218,0.12033],"object_pos_start":[0.54407,0.08173,0.12108],"object_to_goal_dist_end":0.09684,"object_to_goal_dist_start":0.0971,"object_z_max":0.12111,"peak_contact_force":167951.73011,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":120.0,"raw_peak_contact_force":0.24996,"subtask_id":"transport_goal","tcp_end":[0.53295,0.08197,0.14261],"tcp_start":[0.53269,0.08155,0.14289],"tcp_to_object_dist_end":0.02486,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53975,0.05926,0.01604],"object_pos_start":[0.54399,0.08218,0.12033],"object_to_goal_dist_end":0.15808,"object_to_goal_dist_start":0.09684,"object_z_max":0.12033,"peak_contact_force":0.12507,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":737.0,"raw_peak_contact_force":1.34254,"tcp_end":[0.52694,0.08106,0.16641],"tcp_start":[0.53295,0.08197,0.14261],"tcp_to_object_dist_end":0.15249,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```