## Search State

- **Seed**: 9
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.2543 | 0.14 | ✅ accepted |
| 1 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6 | -0.1646 | 0.13 | ✅ accepted |
| 0 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6 | -0.1649 | 0.13 | ✅ accepted |

**Proposal policy**: task_score is 0.14 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.5370249203970084, -0.021318279091244466, 0.03]
- Frozen task target: [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]
- Goal object position: (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5370249203970084, -0.021318279091244466, 0.03)
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
  frozen_object_start: [0.537, -0.0213, 0.03]
  frozen_task_target: [0.6103, 0.2278, 0.2074]
  frozen_object_starts: {'grasp_target': [0.5370249203970084, -0.021318279091244466, 0.03]}
  frozen_targets: {'place_target': [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]}
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
| `object` | offset from object initial position (0.5370249203970084, -0.021318279091244466, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6103148150051562, 0.2277534082920179, 0.2074111944405348) | final destination targets |
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

## Current Skill (Q=-0.254) — your mutation base

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
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: transport_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.3
phases:
- id: approach_to_object
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
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_object
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.03
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: descend_to_grasp
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
      mode: none
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
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
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
  subtask_id: lift_object
- id: transport_to_goal
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_to_goal
- id: descend_to_place
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
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
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
      mode: none

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_to_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=repeat
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=2, strategy=repeat
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.254
- **task_score** (E): 0.142
- **fitness_score**: 0.146  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.400

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_to_object | 0.00 | 0.1755 |
| descend_to_grasp | 1.00 | 0.0251 |
| grasp_object | 1.00 | 0.0000 |
| lift_object | 0.33 | 0.0032 |
| transport_to_goal | 0.00 | 0.0469 |
| descend_to_place | 0.00 | 0.0019 |
| release_object | 1.00 | 0.0272 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_to_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.403, -0.003, 0.155) | (0.515, -0.017, 0.030)→(0.477, -0.018, 0.016) | 0.268→0.294 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.403, -0.003, 0.155)→(0.395, -0.005, 0.178) | (0.477, -0.018, 0.016)→(0.474, -0.020, 0.016) | 0.294→0.296 |
| grasp_object | grasp | 1.00 / step_budget | (0.396, -0.006, 0.178)→(0.396, -0.006, 0.178) | (0.474, -0.020, 0.016)→(0.474, -0.020, 0.016) | 0.296→0.296 |
| lift_object | lift | 0.33 / step_budget | (0.481, -0.044, 0.242)→(0.482, -0.044, 0.242) | (0.474, -0.020, 0.016)→(0.474, -0.020, 0.016) | 0.296→0.296 |
| transport_to_goal | approach | 0.00 / step_budget | (0.482, -0.044, 0.242)→(0.514, -0.014, 0.255) | (0.474, -0.020, 0.016)→(0.474, -0.020, 0.016) | 0.296→0.296 |
| descend_to_place | descend | 0.00 / step_budget | (0.514, -0.014, 0.255)→(0.514, -0.015, 0.257) | (0.474, -0.020, 0.016)→(0.474, -0.020, 0.016) | 0.296→0.296 |
| release_object | release | 1.00 / step_budget | (0.514, -0.015, 0.257)→(0.516, -0.018, 0.283) | (0.474, -0.020, 0.016)→(0.474, -0.020, 0.016) | 0.296→0.296 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.172
- phase_score: 0.221
- phase_breakdown.transport_to_goal_score: 0.000
- phase_breakdown.approach_object_score: 0.264
- phase_breakdown.lift_object_score: 0.512
- phase_breakdown.descend_to_grasp_score: 0.072
- grasp_place_fitness: 0.175

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.175
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.172
- **Median Q (composite search score)**: -0.260
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.503


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
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":241.0,"average_failure_rate":0.70262,"average_mean_iterations":142.95918,"average_solve_count":343.0,"average_success_count":102.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_speed":0.038,"descend_to_grasp.descend_speed":0.00624,"descend_to_place.place_speed":0.04203,"lift_object.lift_speed":0.04539,"transport_to_goal.transport_speed":0.07056},"optimized_scores":{"best_composite_score":-0.27792,"best_fitness_score":0.12208,"best_task_score":0.10531},"replay_outcomes":[{"contacts":{"omitted_contact_groups":11,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.6353,-0.00228,-0.00046],"force_p95":197.52712,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1337.22964,"mean_force":199.22979,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.3953,-0.0023,0.1252]},{"body_a":"world","body_b":"link6","contact_count":534.0,"contact_point_centroid":[0.63633,-0.00561,-0.00013],"force_p95":546.75874,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":972.3969,"mean_force":231.24775,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44508,-0.01179,0.20342]},{"body_a":"world","body_b":"link5","contact_count":9.0,"contact_point_centroid":[0.65579,0.07663,-0.00072],"force_p95":694.25255,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":742.64962,"mean_force":517.13502,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47516,-0.04002,0.17552]},{"body_a":"link5","body_b":"hand","contact_count":139.0,"contact_point_centroid":[0.53226,0.03192,0.15045],"force_p95":243.08801,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":538.85997,"mean_force":125.84014,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48658,-0.04559,0.2183]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.61501,-0.00524,-0.00025],"force_p95":196.65629,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":213.70479,"mean_force":193.70321,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.38797,-0.00568,0.15004]},{"body_a":"link5","body_b":"hand","contact_count":3.0,"contact_point_centroid":[0.54275,-0.01722,0.21634],"force_p95":86.63393,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":89.76212,"mean_force":65.85396,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51268,-0.076,0.30704]},{"body_a":"link5","body_b":"hand","contact_count":3.0,"contact_point_centroid":[0.54285,-0.01717,0.21669],"force_p95":85.5315,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":88.04545,"mean_force":57.47879,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.51273,-0.0761,0.3073]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.60445,-0.00736,-0.00014],"force_p95":81.9272,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":83.83359,"mean_force":74.48548,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.3999,-0.00756,0.18069]},{"body_a":"link5","body_b":"hand","contact_count":136.0,"contact_point_centroid":[0.54283,-0.01757,0.21665],"force_p95":46.42015,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":80.22103,"mean_force":10.41613,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.51284,-0.07675,0.30724]},{"body_a":"grasp_target","body_b":"link7","contact_count":581.0,"contact_point_centroid":[0.52334,-0.01126,0.03281],"force_p95":0.86685,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.41324,"mean_force":0.30599,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.39217,-0.00184,0.11245]},{"body_a":"grasp_target","body_b":"link6","contact_count":124.0,"contact_point_centroid":[0.53889,-0.02267,0.02899],"force_p95":0.92201,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.35126,"mean_force":0.47264,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.3837,-0.00147,0.08739]},{"body_a":"grasp_target","body_b":"hand","contact_count":122.0,"contact_point_centroid":[0.49162,-0.02611,0.04706],"force_p95":2.26392,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.9968,"mean_force":0.8986,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.38511,-0.00146,0.08187]},{"body_a":"world","body_b":"grasp_target","contact_count":3703.0,"contact_point_centroid":[0.50632,-0.02469,-0.00235],"force_p95":0.30067,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.9383,"mean_force":0.16137,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.40833,-0.00217,0.13698]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.49806,-0.02628,-0.00222],"force_p95":0.19545,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20749,"mean_force":0.13752,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.38797,-0.00568,0.15004]},{"body_a":"grasp_target","body_b":"link6","contact_count":542.0,"contact_point_centroid":[0.52592,-0.00688,0.0331],"force_p95":0.19171,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1991,"mean_force":0.11512,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.38308,-0.005,0.13734]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.49739,-0.02643,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.3999,-0.00756,0.18069]}],"total_contact_groups":27},"final_pose_error":0.33458,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.49739,-0.02643,0.01602],"final_tcp_position":[0.51277,-0.07625,0.30748],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50019,-0.02537,0.01602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.3359,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.40515,-0.00366,0.15524],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16996,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49739,-0.02643,0.01602],"object_pos_start":[0.50019,-0.02537,0.01602],"object_to_goal_dist_end":0.33763,"object_to_goal_dist_start":0.3359,"object_z_max":0.01604,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"descend_to_grasp","tcp_end":[0.39956,-0.00751,0.18086],"tcp_start":[0.40515,-0.00366,0.15524],"tcp_to_object_dist_end":0.19262,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.49739,-0.02643,0.01602],"object_pos_start":[0.49739,-0.02643,0.01602],"object_to_goal_dist_end":0.33763,"object_to_goal_dist_start":0.33763,"object_z_max":0.01602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.39996,-0.00759,0.18059],"tcp_start":[0.39996,-0.00759,0.18059],"tcp_to_object_dist_end":0.19217,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":705.0,"n_steps_budget":1000.0,"object_pos_end":[0.49739,-0.02643,0.01602],"object_pos_start":[0.49739,-0.02643,0.01602],"object_to_goal_dist_end":0.33763,"object_to_goal_dist_start":0.33763,"object_z_max":0.01602,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.51265,-0.07596,0.30699],"tcp_start":[0.51244,-0.07581,0.30621],"tcp_to_object_dist_end":0.29555,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49739,-0.02643,0.01602],"object_pos_start":[0.49739,-0.02643,0.01602],"object_to_goal_dist_end":0.33763,"object_to_goal_dist_start":0.33763,"object_z_max":0.01602,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"transport_to_goal","tcp_end":[0.51273,-0.07604,0.30724],"tcp_start":[0.51265,-0.07596,0.30699],"tcp_to_object_dist_end":0.29582,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49739,-0.02643,0.01602],"object_pos_start":[0.49739,-0.02643,0.01602],"object_to_goal_dist_end":0.33763,"object_to_goal_dist_start":0.33763,"object_z_max":0.01602,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.51277,-0.07625,0.30748],"tcp_start":[0.51273,-0.07604,0.30724],"tcp_to_object_dist_end":0.29609,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49739,-0.02643,0.01602],"object_pos_start":[0.49739,-0.02643,0.01602],"object_to_goal_dist_end":0.33763,"object_to_goal_dist_start":0.33763,"object_z_max":0.01602,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.51331,-0.07675,0.33304],"tcp_start":[0.51277,-0.07625,0.30748],"tcp_to_object_dist_end":0.32138,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1e57d18e69439f9d4839513252d085a45363faa5c1c2b52093c9c8149b88bb68`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":255.0,"average_failure_rate":0.64394,"average_mean_iterations":131.20455,"average_solve_count":396.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_speed":0.03038,"descend_to_grasp.descend_speed":0.01796,"descend_to_place.place_speed":0.04504,"lift_object.lift_speed":0.02834,"transport_to_goal.transport_speed":0.0449},"optimized_scores":{"best_composite_score":-0.26001,"best_fitness_score":0.13999,"best_task_score":0.14825},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":885.0,"contact_point_centroid":[0.63225,-0.00269,-0.00047],"force_p95":195.08581,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1657.86811,"mean_force":199.3219,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.39354,-0.00272,0.12855]},{"body_a":"world","body_b":"link6","contact_count":903.0,"contact_point_centroid":[0.63207,-0.00773,-0.00015],"force_p95":515.20133,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":838.04769,"mean_force":230.58396,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44485,-0.01432,0.20747]},{"body_a":"world","body_b":"link5","contact_count":20.0,"contact_point_centroid":[0.65291,0.07219,-0.00092],"force_p95":571.73505,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":575.02626,"mean_force":412.43994,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47895,-0.04511,0.18051]},{"body_a":"link5","body_b":"hand","contact_count":138.0,"contact_point_centroid":[0.52874,0.05171,0.12273],"force_p95":251.14649,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":522.89226,"mean_force":113.61894,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47683,-0.03563,0.18278]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.61121,-0.00614,-0.00025],"force_p95":197.58314,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":215.42793,"mean_force":194.54012,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.38599,-0.00656,0.15262]},{"body_a":"link5","body_b":"hand","contact_count":139.0,"contact_point_centroid":[0.53237,-0.00911,0.14275],"force_p95":78.59532,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":116.59194,"mean_force":73.24107,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.50339,-0.06379,0.24208]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.59998,-0.00874,-0.00014],"force_p95":82.09227,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":83.97886,"mean_force":74.87856,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.39927,-0.00884,0.18494]},{"body_a":"grasp_target","body_b":"link6","contact_count":762.0,"contact_point_centroid":[0.54108,-0.01171,0.02911],"force_p95":0.32581,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.18159,"mean_force":0.16297,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.39229,-0.00252,0.12414]},{"body_a":"grasp_target","body_b":"link7","contact_count":418.0,"contact_point_centroid":[0.52479,-0.00967,0.02962],"force_p95":2.1149,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.7973,"mean_force":0.33232,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.38926,-0.00204,0.10989]},{"body_a":"world","body_b":"grasp_target","contact_count":3763.0,"contact_point_centroid":[0.5149,-0.03093,-0.0027],"force_p95":0.41289,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.30103,"mean_force":0.18046,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.40636,-0.00256,0.13922]},{"body_a":"grasp_target","body_b":"hand","contact_count":22.0,"contact_point_centroid":[0.50375,-0.03091,0.03381],"force_p95":2.2181,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.465,"mean_force":1.1638,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.39216,-0.00174,0.05025]},{"body_a":"grasp_target","body_b":"link6","contact_count":836.0,"contact_point_centroid":[0.53624,-0.0147,0.03246],"force_p95":0.26812,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27479,"mean_force":0.14895,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.38387,-0.00629,0.14794]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50543,-0.03302,-0.00237],"force_p95":0.21472,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2294,"mean_force":0.14769,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.38599,-0.00656,0.15262]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.50379,-0.03367,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.39927,-0.00884,0.18494]},{"body_a":"world","body_b":"grasp_target","contact_count":4040.0,"contact_point_centroid":[0.50379,-0.03367,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44857,-0.01709,0.20561]},{"body_a":"world","body_b":"grasp_target","contact_count":36.0,"contact_point_centroid":[0.50379,-0.03367,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50093,-0.05755,0.2278]}],"total_contact_groups":25},"final_pose_error":0.26528,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.50379,-0.03367,0.01602],"final_tcp_position":[0.50318,-0.05925,0.23442],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50858,-0.03151,0.01602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.2827,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.40218,-0.00418,0.15627],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17815,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50379,-0.03367,0.01602],"object_pos_start":[0.50858,-0.03151,0.01602],"object_to_goal_dist_end":0.28633,"object_to_goal_dist_start":0.2827,"object_z_max":0.01608,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"descend_to_grasp","tcp_end":[0.39893,-0.00878,0.18508],"tcp_start":[0.40218,-0.00418,0.15627],"tcp_to_object_dist_end":0.20049,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50379,-0.03367,0.01602],"object_pos_start":[0.50379,-0.03367,0.01602],"object_to_goal_dist_end":0.28633,"object_to_goal_dist_start":0.28633,"object_z_max":0.01602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.39932,-0.00887,0.18485],"tcp_start":[0.39932,-0.00886,0.18485],"tcp_to_object_dist_end":0.20008,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1010.0,"n_steps_budget":1000.0,"object_pos_end":[0.50379,-0.03367,0.01602],"object_pos_start":[0.50379,-0.03367,0.01602],"object_to_goal_dist_end":0.28633,"object_to_goal_dist_start":0.28633,"object_z_max":0.01602,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.50011,-0.05727,0.22546],"tcp_start":[0.4987,-0.05689,0.22191],"tcp_to_object_dist_end":0.2108,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":9.0,"n_steps_budget":1000.0,"object_pos_end":[0.50379,-0.03367,0.01602],"object_pos_start":[0.50379,-0.03367,0.01602],"object_to_goal_dist_end":0.28633,"object_to_goal_dist_start":0.28633,"object_z_max":0.01602,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"transport_to_goal","tcp_end":[0.50214,-0.058,0.23119],"tcp_start":[0.50011,-0.05727,0.22546],"tcp_to_object_dist_end":0.21655,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.50379,-0.03367,0.01602],"object_pos_start":[0.50379,-0.03367,0.01602],"object_to_goal_dist_end":0.28633,"object_to_goal_dist_start":0.28633,"object_z_max":0.01602,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.50318,-0.05925,0.23442],"tcp_start":[0.50214,-0.058,0.23119],"tcp_to_object_dist_end":0.21989,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50379,-0.03367,0.01602],"object_pos_start":[0.50379,-0.03367,0.01602],"object_to_goal_dist_end":0.28633,"object_to_goal_dist_start":0.28633,"object_z_max":0.01602,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.50556,-0.06911,0.26054],"tcp_start":[0.50318,-0.05925,0.23442],"tcp_to_object_dist_end":0.24709,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `5836f8a66456087ed82e2e1accc6472c2a7681a19bf8e3d54637158aadaafc47`; realized-scene SHA-256: `776f3cbcac69f75f44cb26f0b1a492bbf1ced59f3c5fca79400c3f557c2ce565`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46286,-7e-05,0.03]},{"name":"goal","value":[0.61015,0.15287,0.12219]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.46286,-7e-05,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61015,0.15287,0.12219]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":110.0,"average_failure_rate":0.45833,"average_mean_iterations":94.49583,"average_solve_count":240.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_speed":0.08959,"descend_to_grasp.descend_speed":0.01787,"descend_to_place.place_speed":0.02977,"lift_object.lift_speed":0.05376,"transport_to_goal.transport_speed":0.14392},"optimized_scores":{"best_composite_score":-0.22496,"best_fitness_score":0.17504,"best_task_score":0.17211},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.63158,-2e-05,-0.00046],"force_p95":198.59432,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1368.56894,"mean_force":199.54899,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.39041,-0.00011,0.12263]},{"body_a":"world","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.5264,0.00405,-0.00295],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":462.80066,"mean_force":21.03639,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.37237,-0.00024,0.04988]},{"body_a":"world","body_b":"link6","contact_count":39.0,"contact_point_centroid":[0.65966,0.02414,-0.00025],"force_p95":436.90958,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":441.83121,"mean_force":245.71207,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50944,0.07831,0.21813]},{"body_a":"world","body_b":"link6","contact_count":684.0,"contact_point_centroid":[0.62441,0.00576,-0.00024],"force_p95":262.82267,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":388.78038,"mean_force":229.45446,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4264,0.00082,0.19527]},{"body_a":"link5","body_b":"hand","contact_count":251.0,"contact_point_centroid":[0.5304,0.00664,0.17459],"force_p95":303.93272,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":329.62821,"mean_force":268.84162,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51213,0.07706,0.21996]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.65842,0.02464,-3e-05],"force_p95":259.7034,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":270.38132,"mean_force":172.89801,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.52615,0.09202,0.22713]},{"body_a":"world","body_b":"link6","contact_count":63.0,"contact_point_centroid":[0.65834,0.02589,-6e-05],"force_p95":177.24558,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":257.66337,"mean_force":87.95736,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.52746,0.09066,0.22862]},{"body_a":"link5","body_b":"hand","contact_count":4.0,"contact_point_centroid":[0.52517,0.03046,0.1565],"force_p95":246.09941,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":248.6855,"mean_force":214.44056,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.52615,0.09202,0.22713]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.52689,0.03167,0.16301],"force_p95":206.74634,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":221.99564,"mean_force":163.30803,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5276,0.09116,0.23511]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.61268,9e-05,-0.00026],"force_p95":195.3309,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":204.23765,"mean_force":193.65109,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.38141,-0.00018,0.14402]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.60347,0.00015,-0.00014],"force_p95":84.22106,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":89.92917,"mean_force":74.31976,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.38784,-0.00013,0.16733]},{"body_a":"grasp_target","body_b":"hand","contact_count":39.0,"contact_point_centroid":[0.44373,0.00554,0.04243],"force_p95":3.51633,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.90382,"mean_force":1.52217,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.38291,-0.0002,0.05169]},{"body_a":"world","body_b":"grasp_target","contact_count":3921.0,"contact_point_centroid":[0.42688,0.00125,-0.00213],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.30177,"mean_force":0.13811,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.40244,-8e-05,0.13241]},{"body_a":"grasp_target","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.47532,-0.0027,0.00786],"force_p95":0.26026,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26412,"mean_force":0.14287,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.37112,-0.00025,0.04675]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.42182,0.00146,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.38141,-0.00018,0.14402]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.42182,0.00146,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.38784,-0.00013,0.16733]}],"total_contact_groups":25},"final_pose_error":0.14788,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.42182,0.00146,0.01602],"final_tcp_position":[0.5266,0.09167,0.22775],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.42182,0.00146,0.01602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.26394,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.40025,-0.00011,0.15288],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13856,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.42182,0.00146,0.01602],"object_pos_start":[0.42182,0.00146,0.01602],"object_to_goal_dist_end":0.26394,"object_to_goal_dist_start":0.26394,"object_z_max":0.01602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"descend_to_grasp","tcp_end":[0.38746,-8e-05,0.16754],"tcp_start":[0.40025,-0.00011,0.15288],"tcp_to_object_dist_end":0.15538,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.42182,0.00146,0.01602],"object_pos_start":[0.42182,0.00146,0.01602],"object_to_goal_dist_end":0.26394,"object_to_goal_dist_start":0.26394,"object_z_max":0.01602,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.38791,-0.00016,0.16721],"tcp_start":[0.38791,-0.00016,0.16721],"tcp_to_object_dist_end":0.15495,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":687.0,"n_steps_budget":600.0,"object_pos_end":[0.42182,0.00146,0.01602],"object_pos_start":[0.42182,0.00146,0.01602],"object_to_goal_dist_end":0.26394,"object_to_goal_dist_start":0.26394,"object_z_max":0.01602,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_object","tcp_end":[0.43268,0.00126,0.19432],"tcp_start":[0.43299,0.00101,0.19931],"tcp_to_object_dist_end":0.17863,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":715.0,"n_steps_budget":1000.0,"object_pos_end":[0.42182,0.00146,0.01602],"object_pos_start":[0.42182,0.00146,0.01602],"object_to_goal_dist_end":0.26394,"object_to_goal_dist_start":0.26394,"object_z_max":0.01602,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"transport_to_goal","tcp_end":[0.52576,0.09241,0.22657],"tcp_start":[0.43268,0.00126,0.19432],"tcp_to_object_dist_end":0.25181,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.42182,0.00146,0.01602],"object_pos_start":[0.42182,0.00146,0.01602],"object_to_goal_dist_end":0.26394,"object_to_goal_dist_start":0.26394,"object_z_max":0.01602,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.5266,0.09167,0.22775],"tcp_start":[0.52576,0.09241,0.22657],"tcp_to_object_dist_end":0.25288,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.42182,0.00146,0.01602],"object_pos_start":[0.42182,0.00146,0.01602],"object_to_goal_dist_end":0.26394,"object_to_goal_dist_start":0.26394,"object_z_max":0.01602,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.52821,0.09208,0.25568],"tcp_start":[0.5266,0.09167,0.22775],"tcp_to_object_dist_end":0.27743,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```