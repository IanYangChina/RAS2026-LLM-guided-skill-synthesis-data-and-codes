## Search State

- **Seed**: 1
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4499 | 1.00 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4636 | 1.00 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4636 | 1.00 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | 0.0256 | 0.44 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.0121 | 0.19 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (1.00). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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
- Frozen realised-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`
- Frozen object start: [0.5011821624700257, 0.045046369632593536, 0.03]
- Frozen task target: [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]
- Goal object position: (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5011821624700257, 0.045046369632593536, 0.03)
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
  frozen_object_start: [0.5012, 0.045, 0.03]
  frozen_task_target: [0.5644, 0.2449, 0.1468]
  frozen_object_starts: {'grasp_target': [0.5011821624700257, 0.045046369632593536, 0.03]}
  frozen_targets: {'place_target': [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb

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
| `object` | offset from object initial position (0.5011821624700257, 0.045046369632593536, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5644159612719634, 0.2448649447137244, 0.1467747178015728) | final destination targets |
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

## Current Skill (Q=0.450) — your mutation base

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
  - 0.15
  weight: 0.3
- id: reach_goal
  weight: 0.7
phases:
- id: approach_object
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  subtask_id: reach_object
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_xy_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    grasp_xy_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: reach_object
- id: grasp
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
  guards:
  - id: grasp_hold
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
    - -0.005
- id: lift
  type: lift
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.18
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.18
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: descend_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    place_xy_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    place_xy_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: replace
  guards:
  - id: place_pos
    when: after_phase
    predicate: pose_within_tolerance
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_xy_offset_x: status=consumed; consumers=target.offset.x (replace)
    - grasp_xy_offset_y: status=consumed; consumers=target.offset.y (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_hold, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.18], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_xy_offset_x: status=consumed; consumers=target.offset.x (replace)
    - place_xy_offset_y: status=consumed; consumers=target.offset.y (replace)
  - guards:
    - id=place_pos, when=after_phase, predicate=pose_within_tolerance, on_failure=retry, threshold=0.02
  - retries: max_attempts=1, strategy=offset_target, offset=[0.005, 0.005, 0.0]

## Design Metrics

- **Composite score**: 0.450
- **task_score** (E): 1.000
- **fitness_score**: 0.970  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.0985 |
| descend_to_grasp | 1.00 | 1.00 | 0.1531 |
| grasp | 1.00 | 1.00 | 0.0133 |
| lift | 1.00 | 1.00 | 0.1236 |
| approach_goal | 1.00 | 1.00 | 0.2557 |
| descend_place | 1.00 | 1.00 | 0.0099 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.483, -0.000, 0.208) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 13.581 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.483, -0.000, 0.208)→(0.489, -0.000, 0.055) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 43.667 | 0.161 | 0.186 |
| grasp | grasp | 1.00 / step_budget | (0.489, -0.000, 0.055)→(0.480, -0.000, 0.045) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 39.000 | 0.077 | 0.454 |
| lift | lift | 1.00 / step_budget | (0.480, -0.000, 0.045)→(0.477, -0.000, 0.168) | (0.479, -0.000, 0.026)→(0.478, -0.000, 0.148) | 0.278→0.249 | 1.00 / 39.000 | 0.077 | 0.116 |
| approach_goal | approach | 1.00 / step_budget | (0.477, -0.000, 0.168)→(0.596, 0.186, 0.281) | (0.478, -0.000, 0.148)→(0.598, 0.186, 0.259) | 0.249→0.111 | 1.00 / 37.667 | 0.083 | 0.254 |
| descend_place | descend | 1.00 / step_budget | (0.606, 0.199, 0.178)→(0.607, 0.200, 0.169) | (0.598, 0.186, 0.259)→(0.604, 0.198, 0.156) | 0.111→0.011 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.828
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.077
- phase_breakdown.reach_goal_score: 0.075
- phase_breakdown.reach_object_score: 0.080
- grasp_place_fitness: 0.972

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.972
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.449
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.259


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8110053be9072e64e15984c6424e4a66fe19af4b6c37a60139a43e94cc34ad53`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `46ef03f7b16015a0d14bf26d80c05d326b92c02b0bf759391930f5ab902d1933`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10541,"average_solve_count":370.0,"average_success_count":370.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_speed":0.03116,"descend_place.place_xy_offset_x":0.01208,"descend_place.place_xy_offset_y":0.005,"descend_to_grasp.descend_speed":0.01821,"descend_to_grasp.grasp_xy_offset_x":0.01787,"descend_to_grasp.grasp_xy_offset_y":0.00346,"lift.lift_height":0.11595,"lift.lift_speed":0.04366},"optimized_scores":{"best_composite_score":0.45206,"best_fitness_score":0.97206,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.49796,0.04425,-0.00165],"force_p95":0.44861,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51292,"mean_force":0.20499,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50168,0.04431,0.04455]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3740.0,"contact_point_centroid":[0.49989,0.06329,0.08555],"force_p95":0.11092,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29102,"mean_force":0.05782,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49978,0.04411,0.08374]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3840.0,"contact_point_centroid":[0.49992,0.02495,0.08683],"force_p95":0.10313,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26468,"mean_force":0.0552,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49977,0.04411,0.08462]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3474.0,"contact_point_centroid":[0.56419,0.21613,0.22225],"force_p95":0.09342,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26414,"mean_force":0.05602,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56326,0.23527,0.21979]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2907.0,"contact_point_centroid":[0.56368,0.25394,0.22578],"force_p95":0.09785,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26292,"mean_force":0.06455,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56289,0.23479,0.22328]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50116,0.04498,-0.00206],"force_p95":0.21302,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21407,"mean_force":0.16516,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5039,0.04453,0.0447]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4831.0,"contact_point_centroid":[0.50311,0.02524,0.04544],"force_p95":0.07426,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14528,"mean_force":0.05042,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50278,0.04442,0.04348]},{"body_a":"world","body_b":"grasp_target","contact_count":560.0,"contact_point_centroid":[0.50118,0.04505,-0.00177],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1235,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49953,0.01525,0.25593]},{"body_a":"world","body_b":"grasp_target","contact_count":928.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50423,0.03855,0.13407]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10776.0,"contact_point_centroid":[0.52669,0.15434,0.20258],"force_p95":0.06721,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11657,"mean_force":0.04569,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52678,0.13515,0.20032]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10606.0,"contact_point_centroid":[0.52656,0.11471,0.20182],"force_p95":0.0688,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11608,"mean_force":0.04663,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52637,0.13388,0.1993]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4906.0,"contact_point_centroid":[0.50285,0.06364,0.0453],"force_p95":0.07736,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10417,"mean_force":0.05166,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50278,0.04442,0.04348]}],"total_contact_groups":12},"final_pose_error":0.02078,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56602,0.24336,0.14413],"final_tcp_position":[0.56916,0.24353,0.16515],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":40.49772,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":141.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":40.49772,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":928.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_object","tcp_end":[0.49912,0.03268,0.2072],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18162,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":232.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.21034,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11537.0,"raw_peak_contact_force":0.21407,"subtask_id":"reach_object","tcp_end":[0.51191,0.04518,0.05433],"tcp_start":[0.49912,0.03268,0.2072],"tcp_to_object_dist_end":0.03028,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50107,0.04459,0.02575],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24243,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.07134,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7664.0,"raw_peak_contact_force":0.51292,"tcp_end":[0.50275,0.04442,0.04344],"tcp_start":[0.51191,0.04518,0.05433],"tcp_to_object_dist_end":0.01778,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":187.0,"n_steps_budget":1000.0,"object_pos_end":[0.49729,0.04422,0.11162],"object_pos_start":[0.50107,0.04459,0.02575],"object_to_goal_dist_end":0.21448,"object_to_goal_dist_start":0.24243,"object_z_max":0.11114,"peak_contact_force":0.06787,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21382.0,"raw_peak_contact_force":0.11657,"tcp_end":[0.49943,0.04407,0.12985],"tcp_start":[0.50275,0.04442,0.04344],"tcp_to_object_dist_end":0.01836,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":503.0,"n_steps_budget":1000.0,"object_pos_end":[0.55702,0.22642,0.25475],"object_pos_start":[0.49729,0.04422,0.11162],"object_to_goal_dist_end":0.10979,"object_to_goal_dist_start":0.21448,"object_z_max":0.25448,"peak_contact_force":0.07594,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6381.0,"raw_peak_contact_force":0.26414,"subtask_id":"reach_goal","tcp_end":[0.55695,0.22659,0.27465],"tcp_start":[0.49943,0.04407,0.12985],"tcp_to_object_dist_end":0.0199,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":160.0,"n_steps_budget":1000.0,"object_pos_end":[0.56414,0.2416,0.15358],"object_pos_start":[0.55702,0.22642,0.25475],"object_to_goal_dist_end":0.00755,"object_to_goal_dist_start":0.10979,"object_z_max":0.25499,"peak_contact_force":0.12264,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":560.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.56916,0.24353,0.16515],"tcp_start":[0.56879,0.24223,0.17463],"tcp_to_object_dist_end":0.01276,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1efc3ad2e58ea1c47cd56203c4986b53dab7b80d759e458b85d233ccc9cc04bd`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10053,"average_solve_count":378.0,"average_success_count":378.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_speed":0.02511,"descend_place.place_xy_offset_x":0.00774,"descend_place.place_xy_offset_y":0.00951,"descend_to_grasp.descend_speed":0.03436,"descend_to_grasp.grasp_xy_offset_x":0.01743,"descend_to_grasp.grasp_xy_offset_y":-0.00094,"lift.lift_height":0.16846,"lift.lift_speed":0.0454},"optimized_scores":{"best_composite_score":0.44947,"best_fitness_score":0.96947,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.47294,-0.01925,-0.00167],"force_p95":0.4016,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41907,"mean_force":0.1822,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47822,-0.0196,0.0462]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5143.0,"contact_point_centroid":[0.47713,-0.00028,0.11432],"force_p95":0.09281,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28075,"mean_force":0.06082,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47635,-0.01953,0.11135]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6137.0,"contact_point_centroid":[0.47653,-0.03856,0.11336],"force_p95":0.0898,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28003,"mean_force":0.05341,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47635,-0.01953,0.11112]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3173.0,"contact_point_centroid":[0.62483,0.134,0.26524],"force_p95":0.10002,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23231,"mean_force":0.06056,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.6246,0.15303,0.26398]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2686.0,"contact_point_centroid":[0.62561,0.17219,0.26462],"force_p95":0.1048,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19126,"mean_force":0.06872,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62463,0.15307,0.26375]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47614,-0.02003,-0.00206],"force_p95":0.13823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17282,"mean_force":0.12737,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48033,-0.01964,0.04618]},{"body_a":"world","body_b":"grasp_target","contact_count":528.0,"contact_point_centroid":[0.47616,-0.02015,-0.00176],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12355,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49117,-0.00675,0.25675]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4352.0,"contact_point_centroid":[0.48005,-0.00033,0.04814],"force_p95":0.07522,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12741,"mean_force":0.04937,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47924,-0.01961,0.04508]},{"body_a":"world","body_b":"grasp_target","contact_count":924.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.48356,-0.017,0.13475]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8976.0,"contact_point_centroid":[0.54674,0.08142,0.2521],"force_p95":0.07973,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11732,"mean_force":0.05642,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54578,0.06218,0.24973]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11557.0,"contact_point_centroid":[0.54689,0.04358,0.25217],"force_p95":0.06723,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11494,"mean_force":0.04484,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5461,0.06255,0.25003]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5388.0,"contact_point_centroid":[0.47923,-0.03872,0.04771],"force_p95":0.06494,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08147,"mean_force":0.04094,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47924,-0.01961,0.04508]}],"total_contact_groups":12},"final_pose_error":0.02039,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62932,0.16239,0.18549],"final_tcp_position":[0.63169,0.16256,0.20797],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.41907,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":133.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":924.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_object","tcp_end":[0.48121,-0.01453,0.20841],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18254,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":231.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13536,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11540.0,"raw_peak_contact_force":0.17282,"subtask_id":"reach_object","tcp_end":[0.48803,-0.01977,0.05501],"tcp_start":[0.48121,-0.01453,0.20841],"tcp_to_object_dist_end":0.03133,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47604,-0.01957,0.02576],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28823,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.07834,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11360.0,"raw_peak_contact_force":0.41907,"tcp_end":[0.47921,-0.01961,0.04505],"tcp_start":[0.48803,-0.01977,0.05501],"tcp_to_object_dist_end":0.01954,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":288.0,"n_steps_budget":1000.0,"object_pos_end":[0.47412,-0.01938,0.16335],"object_pos_start":[0.47604,-0.01957,0.02576],"object_to_goal_dist_end":0.23946,"object_to_goal_dist_start":0.28823,"object_z_max":0.16287,"peak_contact_force":0.08061,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20533.0,"raw_peak_contact_force":0.11732,"tcp_end":[0.4764,-0.01952,0.18398],"tcp_start":[0.47921,-0.01961,0.04505],"tcp_to_object_dist_end":0.02076,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":528.0,"n_steps_budget":1000.0,"object_pos_end":[0.61817,0.14357,0.29658],"object_pos_start":[0.47412,-0.01938,0.16335],"object_to_goal_dist_end":0.10852,"object_to_goal_dist_start":0.23946,"object_z_max":0.29633,"peak_contact_force":0.07839,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5859.0,"raw_peak_contact_force":0.23231,"subtask_id":"reach_goal","tcp_end":[0.61724,0.14366,0.31862],"tcp_start":[0.4764,-0.01952,0.18398],"tcp_to_object_dist_end":0.02206,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":158.0,"n_steps_budget":1000.0,"object_pos_end":[0.62699,0.16033,0.19501],"object_pos_start":[0.61817,0.14357,0.29658],"object_to_goal_dist_end":0.00677,"object_to_goal_dist_start":0.10852,"object_z_max":0.29671,"peak_contact_force":0.12262,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":528.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.63169,0.16256,0.20797],"tcp_start":[0.63101,0.16093,0.21777],"tcp_to_object_dist_end":0.01396,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `37495cb43897015e78e007c86af160d11c8460c1ce7249e5c03dce38206c0daf`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18108,"average_solve_count":370.0,"average_success_count":370.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_speed":0.01908,"descend_place.place_xy_offset_x":-0.00429,"descend_place.place_xy_offset_y":-0.01183,"descend_to_grasp.descend_speed":0.03085,"descend_to_grasp.grasp_xy_offset_x":0.01033,"descend_to_grasp.grasp_xy_offset_y":-0.00153,"lift.lift_height":0.175,"lift.lift_speed":0.06668},"optimized_scores":{"best_composite_score":0.44816,"best_fitness_score":0.96816,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":68.0,"contact_point_centroid":[0.45629,-0.02552,-0.00156],"force_p95":0.38466,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42951,"mean_force":0.13216,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45611,-0.0258,0.04739]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6161.0,"contact_point_centroid":[0.45493,-0.04469,0.11726],"force_p95":0.08841,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29435,"mean_force":0.05334,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45429,-0.0257,0.11522]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4896.0,"contact_point_centroid":[0.45533,-0.00647,0.1186],"force_p95":0.09953,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2943,"mean_force":0.06421,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45428,-0.0257,0.1167]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3220.0,"contact_point_centroid":[0.61681,0.17191,0.19251],"force_p95":0.10825,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2654,"mean_force":0.06223,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61668,0.19094,0.1917]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2737.0,"contact_point_centroid":[0.61753,0.21006,0.19207],"force_p95":0.11456,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2417,"mean_force":0.07093,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61668,0.19094,0.1917]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45855,-0.02624,-0.00205],"force_p95":0.13826,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17078,"mean_force":0.12692,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45822,-0.02588,0.0472]},{"body_a":"world","body_b":"grasp_target","contact_count":560.0,"contact_point_centroid":[0.45856,-0.02632,-0.00177],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1235,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48493,-0.00903,0.25591]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4113.0,"contact_point_centroid":[0.4582,-0.00655,0.0479],"force_p95":0.07837,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12938,"mean_force":0.05233,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45717,-0.02584,0.0462]},{"body_a":"world","body_b":"grasp_target","contact_count":920.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46605,-0.02251,0.13471]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10700.0,"contact_point_centroid":[0.53308,0.06203,0.22027],"force_p95":0.07453,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11488,"mean_force":0.04914,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53294,0.08102,0.21914]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9095.0,"contact_point_centroid":[0.53392,0.10016,0.22009],"force_p95":0.08174,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09722,"mean_force":0.05656,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53294,0.08102,0.21914]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5382.0,"contact_point_centroid":[0.45808,-0.04489,0.04857],"force_p95":0.06508,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08045,"mean_force":0.04063,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45718,-0.02584,0.0462]}],"total_contact_groups":12},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62186,0.19316,0.10775],"final_tcp_position":[0.61938,0.19362,0.13281],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.42951,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":141.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":920.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_object","tcp_end":[0.46802,-0.01937,0.20697],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18133,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":230.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.1372,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11295.0,"raw_peak_contact_force":0.17078,"subtask_id":"reach_object","tcp_end":[0.46565,-0.02609,0.0553],"tcp_start":[0.46802,-0.01937,0.20697],"tcp_to_object_dist_end":0.03012,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45846,-0.02582,0.02578],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30339,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.08257,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11125.0,"raw_peak_contact_force":0.42951,"tcp_end":[0.45715,-0.02584,0.04617],"tcp_start":[0.46565,-0.02609,0.0553],"tcp_to_object_dist_end":0.02043,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":288.0,"n_steps_budget":1000.0,"object_pos_end":[0.46162,-0.02581,0.17008],"object_pos_start":[0.45846,-0.02582,0.02578],"object_to_goal_dist_end":0.29376,"object_to_goal_dist_start":0.30339,"object_z_max":0.16958,"peak_contact_force":0.08275,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19795.0,"raw_peak_contact_force":0.11488,"tcp_end":[0.4544,-0.02568,0.1914],"tcp_start":[0.45715,-0.02584,0.04617],"tcp_to_object_dist_end":0.02251,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":535.0,"n_steps_budget":1000.0,"object_pos_end":[0.61912,0.18772,0.22582],"object_pos_start":[0.46162,-0.02581,0.17008],"object_to_goal_dist_end":0.1141,"object_to_goal_dist_start":0.29376,"object_z_max":0.22572,"peak_contact_force":0.09364,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5957.0,"raw_peak_contact_force":0.2654,"subtask_id":"reach_goal","tcp_end":[0.61368,0.18803,0.24982],"tcp_start":[0.4544,-0.02568,0.1914],"tcp_to_object_dist_end":0.02461,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":161.0,"n_steps_budget":1000.0,"object_pos_end":[0.62086,0.19229,0.11794],"object_pos_start":[0.61912,0.18772,0.22582],"object_to_goal_dist_end":0.01882,"object_to_goal_dist_start":0.1141,"object_z_max":0.22583,"peak_contact_force":0.12264,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":560.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.61938,0.19362,0.13281],"tcp_start":[0.61965,0.19304,0.14304],"tcp_to_object_dist_end":0.015,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```