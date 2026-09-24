## Search State

- **Seed**: 2
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.3599 | 1.00 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2200 | 0.36 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.0009 | 0.48 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.1488 | 0.40 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.0234 | 0.33 | ❌ rejected |

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

## Current Skill (Q=0.360) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: grasp_object
  anchor: object
  target_entity: object
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: approach_goal
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: place_object
  target_entity: object
  weight: 0.2
phases:
- id: approach_above_object
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descent_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_z_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: grasp_object
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
  - id: grasp_guard
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
  subtask_id: grasp_object
- id: lift
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_guard
    when: after_phase
    predicate: object_lifted
    threshold: 0.03
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
  subtask_id: lift_object
- id: approach_above_goal
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
    approach_goal_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_goal_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_goal
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    place_z_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: place_object

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descent_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_z_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_guard, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_guard, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.03
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **approach_above_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_goal_height: status=consumed; consumers=target.offset.z (replace)
    - approach_goal_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: 0.360
- **task_score** (E): 1.000
- **fitness_score**: 0.980  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.620

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_object | 1.00 | 1.00 | 0.0937 |
| descend_to_grasp | 1.00 | 1.00 | 0.1809 |
| grasp | 1.00 | 1.00 | 0.0116 |
| lift | 0.67 | 1.00 | 0.0970 |
| approach_above_goal | 0.67 | 1.00 | 0.2752 |
| descend_to_place | 1.00 | 1.00 | 0.1001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, -0.010, 0.215) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.122 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.495, -0.010, 0.215)→(0.489, -0.015, 0.035) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.489, -0.015, 0.035)→(0.480, -0.015, 0.026) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 44.667 | 0.137 | 0.190 |
| lift | lift | 0.67 / step_budget | (0.480, -0.015, 0.026)→(0.476, -0.015, 0.123) | (0.493, -0.015, 0.026)→(0.486, -0.015, 0.114) | 0.281→0.251 | 1.00 / 43.000 | 0.071 | 0.651 |
| approach_above_goal | approach | 0.67 / step_budget | (0.476, -0.015, 0.123)→(0.620, 0.159, 0.270) | (0.486, -0.015, 0.114)→(0.628, 0.159, 0.254) | 0.251→0.091 | 1.00 / 30.667 | 0.091 | 0.112 |
| descend_to_place | descend | 1.00 / step_budget | (0.620, 0.159, 0.270)→(0.630, 0.172, 0.172) | (0.628, 0.159, 0.254)→(0.636, 0.172, 0.153) | 0.091→0.013 | 1.00 / 28.667 | 0.103 | 0.186 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.446
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.487
- phase_breakdown.approach_object_score: 0.132
- phase_breakdown.grasp_object_score: 0.798
- phase_breakdown.lift_object_score: 0.320
- phase_breakdown.approach_goal_score: 0.363
- phase_breakdown.place_object_score: 0.820
- grasp_place_fitness: 0.982

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.982
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.361
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: lift.lift_speed
- **Final σ (mean)**: 0.328


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31624,"average_solve_count":234.0,"average_success_count":234.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.1544,"approach_above_goal.approach_goal_speed":0.02783,"approach_above_object.approach_height":0.14897,"approach_above_object.approach_speed":0.23976,"descend_to_grasp.descent_speed":0.11011,"descend_to_grasp.grasp_z_tolerance":0.01138,"descend_to_place.place_speed":0.07062,"descend_to_place.place_z_tolerance":0.01424,"lift.lift_height":0.12408,"lift.lift_speed":0.05683},"optimized_scores":{"best_composite_score":0.36081,"best_fitness_score":0.98081,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":163.0,"contact_point_centroid":[0.47177,-0.01915,-0.00116],"force_p95":0.4718,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6532,"mean_force":0.10354,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46256,-0.01952,0.02868]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20704.0,"contact_point_centroid":[0.45989,-0.00029,0.07907],"force_p95":0.07119,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29115,"mean_force":0.04905,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46003,-0.01944,0.0771]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20508.0,"contact_point_centroid":[0.4599,-0.03861,0.07757],"force_p95":0.07238,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29081,"mean_force":0.04975,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46004,-0.01944,0.07581]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02002,-0.00205],"force_p95":0.1384,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18946,"mean_force":0.12698,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46526,-0.01958,0.02818]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4558.0,"contact_point_centroid":[0.61487,0.16147,0.2514],"force_p95":0.09893,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17627,"mean_force":0.07223,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61267,0.14236,0.24956]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6512.0,"contact_point_centroid":[0.61445,0.12403,0.24825],"force_p95":0.08615,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14766,"mean_force":0.05342,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61304,0.14277,0.2476]},{"body_a":"world","body_b":"grasp_target","contact_count":768.0,"contact_point_centroid":[0.47616,-0.02015,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12326,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.48929,-0.0076,0.25067]},{"body_a":"world","body_b":"grasp_target","contact_count":2036.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47387,-0.01784,0.11539]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20151.0,"contact_point_centroid":[0.53068,0.03716,0.21241],"force_p95":0.07349,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1154,"mean_force":0.0495,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.53,0.05615,0.21193]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17803.0,"contact_point_centroid":[0.52832,0.07255,0.20956],"force_p95":0.08392,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10917,"mean_force":0.05545,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.52734,0.05342,0.20863]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5062.0,"contact_point_centroid":[0.46382,-0.00033,0.02961],"force_p95":0.06597,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09497,"mean_force":0.04286,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46415,-0.01955,0.02708]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5162.0,"contact_point_centroid":[0.46406,-0.03881,0.02904],"force_p95":0.06669,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08302,"mean_force":0.04304,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46415,-0.01955,0.02708]}],"total_contact_groups":12},"final_pose_error":0.00984,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62675,0.15497,0.17666],"final_tcp_position":[0.62445,0.15474,0.19534],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.6532,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":193.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":768.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.47835,-0.01603,0.19824],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17229,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":509.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2036.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.47197,-0.01972,0.03484],"tcp_start":[0.47835,-0.01603,0.19824],"tcp_to_object_dist_end":0.00977,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.0196,0.02581],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28823,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13616,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12024.0,"raw_peak_contact_force":0.18946,"subtask_id":"grasp_object","tcp_end":[0.46412,-0.01955,0.02705],"tcp_start":[0.47197,-0.01972,0.03484],"tcp_to_object_dist_end":0.01198,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47008,-0.01939,0.11518],"object_pos_start":[0.47603,-0.0196,0.02581],"object_to_goal_dist_end":0.25204,"object_to_goal_dist_start":0.28823,"object_z_max":0.11511,"peak_contact_force":0.0693,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41375.0,"raw_peak_contact_force":0.6532,"subtask_id":"lift_object","tcp_end":[0.46005,-0.01943,0.1245],"tcp_start":[0.46412,-0.01955,0.02705],"tcp_to_object_dist_end":0.01368,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61072,0.13202,0.28616],"object_pos_start":[0.47008,-0.01939,0.11518],"object_to_goal_dist_end":0.10204,"object_to_goal_dist_start":0.25204,"object_z_max":0.286,"peak_contact_force":0.09214,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37954.0,"raw_peak_contact_force":0.1154,"subtask_id":"approach_goal","tcp_end":[0.60351,0.13165,0.30304],"tcp_start":[0.46005,-0.01943,0.1245],"tcp_to_object_dist_end":0.01836,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":333.0,"n_steps_budget":1000.0,"object_pos_end":[0.62675,0.15497,0.17666],"object_pos_start":[0.61072,0.13202,0.28616],"object_to_goal_dist_end":0.01477,"object_to_goal_dist_start":0.10204,"object_z_max":0.28625,"peak_contact_force":0.09411,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11070.0,"raw_peak_contact_force":0.17627,"subtask_id":"place_object","tcp_end":[0.62445,0.15474,0.19534],"tcp_start":[0.60351,0.13165,0.30304],"tcp_to_object_dist_end":0.01883,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41404,"average_solve_count":285.0,"average_success_count":285.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.11458,"approach_above_goal.approach_goal_speed":0.07492,"approach_above_object.approach_height":0.2422,"approach_above_object.approach_speed":0.15781,"descend_to_grasp.descent_speed":0.08312,"descend_to_grasp.grasp_z_tolerance":0.01215,"descend_to_place.place_speed":0.04946,"descend_to_place.place_z_tolerance":0.00927,"lift.lift_height":0.13104,"lift.lift_speed":0.03},"optimized_scores":{"best_composite_score":0.36211,"best_fitness_score":0.98211,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":171.0,"contact_point_centroid":[0.4536,-0.02455,-0.00125],"force_p95":0.46508,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56162,"mean_force":0.1259,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44601,-0.02529,0.02947]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20603.0,"contact_point_centroid":[0.44358,-0.04435,0.07961],"force_p95":0.07167,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24733,"mean_force":0.04902,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44357,-0.02519,0.07755]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20606.0,"contact_point_centroid":[0.44355,-0.00602,0.07964],"force_p95":0.07221,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23558,"mean_force":0.04871,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44357,-0.02519,0.07755]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02617,-0.00209],"force_p95":0.14812,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21931,"mean_force":0.12949,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44864,-0.02538,0.02898]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3637.0,"contact_point_centroid":[0.62314,0.18204,0.16846],"force_p95":0.09984,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19382,"mean_force":0.07255,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62066,0.20097,0.16793]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4422.0,"contact_point_centroid":[0.62377,0.21963,0.17001],"force_p95":0.08532,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18522,"mean_force":0.06177,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62055,0.20084,0.16951]},{"body_a":"world","body_b":"grasp_target","contact_count":316.0,"contact_point_centroid":[0.45856,-0.02632,-0.0016],"force_p95":0.13825,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12436,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.48756,-0.00704,0.29057]},{"body_a":"world","body_b":"grasp_target","contact_count":3104.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46326,-0.02065,0.15588]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19052.0,"contact_point_centroid":[0.53229,0.06988,0.1716],"force_p95":0.07278,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11893,"mean_force":0.04981,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.53215,0.08903,0.16991]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5277.0,"contact_point_centroid":[0.4469,-0.00616,0.02922],"force_p95":0.06667,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11128,"mean_force":0.04102,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44756,-0.02534,0.02796]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19791.0,"contact_point_centroid":[0.53378,0.10996,0.17234],"force_p95":0.0693,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10417,"mean_force":0.04794,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.53357,0.09083,0.17064]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5071.0,"contact_point_centroid":[0.44755,-0.04465,0.02967],"force_p95":0.07081,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08586,"mean_force":0.04402,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44757,-0.02534,0.02796]}],"total_contact_groups":12},"final_pose_error":0.00991,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.63357,0.20507,0.10408],"final_tcp_position":[0.62412,0.20501,0.12133],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.56162,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":80.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02596],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30367,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12218,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":316.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.47345,-0.01575,0.27968],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25438,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":776.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02596],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30367,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3104.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.45517,-0.0256,0.0352],"tcp_start":[0.47345,-0.01575,0.27968],"tcp_to_object_dist_end":0.00982,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02543,0.02569],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30313,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14562,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12148.0,"raw_peak_contact_force":0.21931,"subtask_id":"grasp_object","tcp_end":[0.44754,-0.02534,0.02793],"tcp_start":[0.45517,-0.0256,0.0352],"tcp_to_object_dist_end":0.01114,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45165,-0.02518,0.11628],"object_pos_start":[0.45844,-0.02543,0.02569],"object_to_goal_dist_end":0.29382,"object_to_goal_dist_start":0.30313,"object_z_max":0.11618,"peak_contact_force":0.06911,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41380.0,"raw_peak_contact_force":0.56162,"subtask_id":"lift_object","tcp_end":[0.44361,-0.02518,0.12502],"tcp_start":[0.44754,-0.02534,0.02793],"tcp_to_object_dist_end":0.01188,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":963.0,"n_steps_budget":1000.0,"object_pos_end":[0.62911,0.19816,0.20098],"object_pos_start":[0.45165,-0.02518,0.11628],"object_to_goal_dist_end":0.08745,"object_to_goal_dist_start":0.29382,"object_z_max":0.20092,"peak_contact_force":0.08766,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38843.0,"raw_peak_contact_force":0.11893,"subtask_id":"approach_goal","tcp_end":[0.61946,0.19779,0.21565],"tcp_start":[0.44361,-0.02518,0.12502],"tcp_to_object_dist_end":0.01756,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":273.0,"n_steps_budget":1000.0,"object_pos_end":[0.63357,0.20507,0.10408],"object_pos_start":[0.62911,0.19816,0.20098],"object_to_goal_dist_end":0.01107,"object_to_goal_dist_start":0.08745,"object_z_max":0.20098,"peak_contact_force":0.09528,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8059.0,"raw_peak_contact_force":0.19382,"subtask_id":"place_object","tcp_end":[0.62412,0.20501,0.12133],"tcp_start":[0.61946,0.19779,0.21565],"tcp_to_object_dist_end":0.01967,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10526,"average_solve_count":266.0,"average_success_count":266.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.12176,"approach_above_goal.approach_goal_speed":0.02432,"approach_above_object.approach_height":0.12049,"approach_above_object.approach_speed":0.22446,"descend_to_grasp.descent_speed":0.0574,"descend_to_grasp.grasp_z_tolerance":0.00841,"descend_to_place.place_speed":0.0546,"descend_to_place.place_z_tolerance":0.00975,"lift.lift_height":0.15624,"lift.lift_speed":0.05996},"optimized_scores":{"best_composite_score":0.35676,"best_fitness_score":0.97676,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":204.0,"contact_point_centroid":[0.53891,0.0007,-0.00113],"force_p95":0.49194,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73801,"mean_force":0.11809,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52766,0.00082,0.02551]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18589.0,"contact_point_centroid":[0.52611,-0.01832,0.07449],"force_p95":0.07825,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32947,"mean_force":0.0549,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52513,0.00078,0.07251]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19118.0,"contact_point_centroid":[0.5261,0.01985,0.07326],"force_p95":0.07757,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31597,"mean_force":0.05376,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52515,0.00078,0.07145]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3747.0,"contact_point_centroid":[0.64096,0.17006,0.24396],"force_p95":0.09285,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18852,"mean_force":0.06725,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63959,0.15128,0.24612]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3493.0,"contact_point_centroid":[0.64031,0.1323,0.24675],"force_p95":0.09875,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16482,"mean_force":0.07093,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63952,0.15114,0.2482]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00098,-0.00203],"force_p95":0.13176,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1605,"mean_force":0.12529,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53093,0.00088,0.02537]},{"body_a":"world","body_b":"grasp_target","contact_count":1004.0,"contact_point_centroid":[0.54431,0.00113,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.51608,0.00044,0.23476]},{"body_a":"world","body_b":"grasp_target","contact_count":1764.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53483,0.00094,0.09947]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53076,-0.01834,0.02663],"force_p95":0.07604,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11028,"mean_force":0.0517,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52968,0.00086,0.02394]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19485.0,"contact_point_centroid":[0.58141,0.05622,0.20488],"force_p95":0.07454,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10099,"mean_force":0.0508,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.58032,0.07504,0.20455]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15155.0,"contact_point_centroid":[0.57965,0.09102,0.20197],"force_p95":0.09255,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09992,"mean_force":0.06409,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.57783,0.07189,0.20077]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53069,0.01994,0.02575],"force_p95":0.06805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09672,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52968,0.00086,0.02394]}],"total_contact_groups":12},"final_pose_error":0.0097,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64898,0.15492,0.17973],"final_tcp_position":[0.64266,0.15539,0.19899],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.73801,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":252.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1004.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.5343,0.00091,0.16755],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14188,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":441.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1764.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.53837,0.00102,0.03399],"tcp_start":[0.5343,0.00091,0.16755],"tcp_to_object_dist_end":0.00993,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54415,0.00073,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12965,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.1605,"subtask_id":"grasp_object","tcp_end":[0.52965,0.00086,0.0239],"tcp_start":[0.53837,0.00102,0.03399],"tcp_to_object_dist_end":0.01464,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53675,0.00079,0.11126],"object_pos_start":[0.54415,0.00073,0.02588],"object_to_goal_dist_end":0.20835,"object_to_goal_dist_start":0.25053,"object_z_max":0.11116,"peak_contact_force":0.07383,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37911.0,"raw_peak_contact_force":0.73801,"subtask_id":"lift_object","tcp_end":[0.52527,0.00079,0.12016],"tcp_start":[0.52965,0.00086,0.0239],"tcp_to_object_dist_end":0.01452,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.64543,0.14815,0.27518],"object_pos_start":[0.53675,0.00079,0.11126],"object_to_goal_dist_end":0.08469,"object_to_goal_dist_start":0.20835,"object_z_max":0.27503,"peak_contact_force":0.09295,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34640.0,"raw_peak_contact_force":0.10099,"subtask_id":"approach_goal","tcp_end":[0.6382,0.14799,0.29216],"tcp_start":[0.52527,0.00079,0.12016],"tcp_to_object_dist_end":0.01846,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":257.0,"n_steps_budget":1000.0,"object_pos_end":[0.64898,0.15492,0.17973],"object_pos_start":[0.64543,0.14815,0.27518],"object_to_goal_dist_end":0.01188,"object_to_goal_dist_start":0.08469,"object_z_max":0.27522,"peak_contact_force":0.12077,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7240.0,"raw_peak_contact_force":0.18852,"subtask_id":"place_object","tcp_end":[0.64266,0.15539,0.19899],"tcp_start":[0.6382,0.14799,0.29216],"tcp_to_object_dist_end":0.02028,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```