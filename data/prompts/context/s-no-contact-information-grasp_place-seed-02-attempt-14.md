## Search State

- **Seed**: 2
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2600 | 1.00 | ✅ accepted |
| 13 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.2599 | 1.00 | ✅ accepted |
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.1950 | 0.94 | ✅ accepted |
| 11 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | force_threshold_switch | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 11 | 0.0195 | 0.39 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.1713 | 0.73 | ✅ accepted |

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

## Current Skill (Q=0.260) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.2
- id: grasp_object
  anchor: object
  target_entity: object
  metric: contact
  weight: 0.3
- id: lift_clearance
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.18
  weight: 0.2
- id: place_at_goal
  target_entity: object
  weight: 0.3
phases:
- id: approach_above
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
    - 0.14
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    approach_offset_z:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.14
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
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.03
      - 0.12
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
    descend_tolerance:
      type: scalar
      range:
      - 0.008
      - 0.03
      default: 0.012
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
  subtask_id: grasp_object
- id: grasp_close
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
  - id: bilateral_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: lift_up
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
      distance: 0.18
      axis: world_z
      mode: add_to_offset
      sign: positive
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
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
    lift_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.025
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: object_lifted
    when: after_phase
    predicate: object_lifted
    threshold: 0.03
    on_failure: abort
  subtask_id: lift_clearance
- id: transport_to_goal
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
    - 0.08
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    transport_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: object_retained
    when: after_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: abort
  subtask_id: place_at_goal
- id: place_at_goal
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
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    place_tolerance:
      type: scalar
      range:
      - 0.008
      - 0.03
      default: 0.012
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    place_z_offset:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: object_still_grasped
    when: after_phase
    predicate: object_lifted
    threshold: 0.01
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: place_at_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.14]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_offset_z: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **grasp_close** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=bilateral_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=repeat
- **lift_up** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.18, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
    - lift_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=object_lifted, when=after_phase, predicate=object_lifted, on_failure=abort, threshold=0.03
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.08]
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=object_retained, when=after_phase, predicate=object_lifted, on_failure=abort, threshold=0.02
- **place_at_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=object_still_grasped, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.01
  - retries: max_attempts=1, strategy=reduce_speed

## Design Metrics

- **Composite score**: 0.260
- **task_score** (E): 1.000
- **fitness_score**: 0.980  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.720

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_above | 1.00 | 0.1160 |
| descend_to_grasp | 1.00 | 0.1568 |
| grasp_close | 1.00 | 0.0114 |
| lift_up | 1.00 | 0.0991 |
| transport_to_goal | 1.00 | 0.2447 |
| place_at_goal | 1.00 | 0.0479 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.491, -0.013, 0.191) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.491, -0.013, 0.191)→(0.488, -0.015, 0.035) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 |
| grasp_close | grasp | 1.00 / step_budget | (0.488, -0.015, 0.035)→(0.480, -0.015, 0.026) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 |
| lift_up | lift | 1.00 / step_budget | (0.480, -0.015, 0.026)→(0.478, -0.015, 0.125) | (0.493, -0.015, 0.026)→(0.496, -0.015, 0.124) | 0.281→0.244 |
| transport_to_goal | approach | 1.00 / step_budget | (0.478, -0.015, 0.125)→(0.618, 0.154, 0.223) | (0.496, -0.015, 0.124)→(0.634, 0.154, 0.212) | 0.244→0.052 |
| place_at_goal | descend | 1.00 / step_budget | (0.618, 0.154, 0.223)→(0.627, 0.166, 0.178) | (0.634, 0.154, 0.212)→(0.644, 0.166, 0.164) | 0.052→0.013 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.435
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.598
- phase_breakdown.approach_object_score: 0.401
- phase_breakdown.place_at_goal_score: 0.596
- phase_breakdown.grasp_object_score: 1.000
- phase_breakdown.lift_clearance_score: 0.195
- grasp_place_fitness: 0.982

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.982
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.261
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.300


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.07362,"average_solve_count":326.0,"average_success_count":326.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_offset_z":0.14054,"approach_above.approach_speed":0.05136,"descend_to_grasp.descend_speed":0.04316,"descend_to_grasp.descend_tolerance":0.01084,"lift_up.lift_height":0.15234,"lift_up.lift_speed":0.09688,"lift_up.lift_tolerance":0.04825,"place_at_goal.place_speed":0.03212,"place_at_goal.place_tolerance":0.02685,"place_at_goal.place_z_offset":-0.00961,"transport_to_goal.transport_speed":0.03248,"transport_to_goal.transport_tolerance":0.03863},"optimized_scores":{"best_composite_score":0.26054,"best_fitness_score":0.98054,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":61.0,"contact_point_centroid":[0.47354,-0.01953,-0.00149],"force_p95":0.64501,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66617,"mean_force":0.30872,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.46272,-0.01961,0.0292]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2353.0,"contact_point_centroid":[0.4619,-0.00035,0.07526],"force_p95":0.11687,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31189,"mean_force":0.06456,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.46153,-0.01955,0.07268]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2614.0,"contact_point_centroid":[0.46192,-0.03871,0.07587],"force_p95":0.10451,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29734,"mean_force":0.05907,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.46154,-0.01955,0.07397]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":942.0,"contact_point_centroid":[0.62023,0.12451,0.23037],"force_p95":0.11929,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23278,"mean_force":0.08628,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.61472,0.14306,0.22846]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":960.0,"contact_point_centroid":[0.62014,0.16156,0.23079],"force_p95":0.12221,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22385,"mean_force":0.08678,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.61458,0.1429,0.22914]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02002,-0.00204],"force_p95":0.1357,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17594,"mean_force":0.12629,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.46523,-0.01967,0.02927]},{"body_a":"world","body_b":"grasp_target","contact_count":1572.0,"contact_point_centroid":[0.47616,-0.02015,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12294,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48721,-0.00856,0.24048]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5514.0,"contact_point_centroid":[0.53397,0.07272,0.186],"force_p95":0.10643,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13053,"mean_force":0.06755,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53095,0.05396,0.18476]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5724.0,"contact_point_centroid":[0.53224,0.03347,0.18441],"force_p95":0.10438,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12819,"mean_force":0.06836,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52921,0.05213,0.18337]},{"body_a":"world","body_b":"grasp_target","contact_count":1904.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4723,-0.01875,0.10754]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5069.0,"contact_point_centroid":[0.46367,-0.0004,0.03124],"force_p95":0.06638,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09269,"mean_force":0.04289,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.46414,-0.01964,0.02819]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5397.0,"contact_point_centroid":[0.46357,-0.0389,0.03063],"force_p95":0.06481,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08743,"mean_force":0.04121,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.46414,-0.01964,0.0282]}],"total_contact_groups":12},"final_pose_error":0.02638,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.63938,0.14961,0.19045],"final_tcp_position":[0.62057,0.1496,0.20246],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"phases":[{"n_steps":394.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.47546,-0.0178,0.17995],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15395,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":476.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_object","tcp_end":[0.47179,-0.01982,0.03584],"tcp_start":[0.47546,-0.0178,0.17995],"tcp_to_object_dist_end":0.01076,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47604,-0.01967,0.02584],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28825,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.46411,-0.01964,0.02816],"tcp_start":[0.47179,-0.01982,0.03584],"tcp_to_object_dist_end":0.01216,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":127.0,"n_steps_budget":990.0,"object_pos_end":[0.47884,-0.01939,0.13003],"object_pos_start":[0.47604,-0.01967,0.02584],"object_to_goal_dist_end":0.24243,"object_to_goal_dist_start":0.28825,"object_z_max":0.12915,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_clearance","tcp_end":[0.46243,-0.01952,0.13245],"tcp_start":[0.46411,-0.01964,0.02816],"tcp_to_object_dist_end":0.01658,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":376.0,"n_steps_budget":1000.0,"object_pos_end":[0.62694,0.13771,0.23596],"object_pos_start":[0.47884,-0.01939,0.13003],"object_to_goal_dist_end":0.05092,"object_to_goal_dist_start":0.24243,"object_z_max":0.23567,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.61043,0.13792,0.24622],"tcp_start":[0.46243,-0.01952,0.13245],"tcp_to_object_dist_end":0.01943,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":82.0,"n_steps_budget":1000.0,"object_pos_end":[0.63938,0.14961,0.19045],"object_pos_start":[0.62694,0.13771,0.23596],"object_to_goal_dist_end":0.01247,"object_to_goal_dist_start":0.05092,"object_z_max":0.23639,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_at_goal","tcp_end":[0.62057,0.1496,0.20246],"tcp_start":[0.61043,0.13792,0.24622],"tcp_to_object_dist_end":0.02232,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11284,"average_solve_count":257.0,"average_success_count":257.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_offset_z":0.15641,"approach_above.approach_speed":0.18347,"descend_to_grasp.descend_speed":0.0558,"descend_to_grasp.descend_tolerance":0.00827,"lift_up.lift_height":0.14149,"lift_up.lift_speed":0.15545,"lift_up.lift_tolerance":0.03874,"place_at_goal.place_speed":0.02943,"place_at_goal.place_tolerance":0.02069,"place_at_goal.place_z_offset":0.00662,"transport_to_goal.transport_speed":0.05667,"transport_to_goal.transport_tolerance":0.0316},"optimized_scores":{"best_composite_score":0.2618,"best_fitness_score":0.9818,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":57.0,"contact_point_centroid":[0.45497,-0.02562,-0.00151],"force_p95":0.82285,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.84176,"mean_force":0.35348,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.44552,-0.02561,0.02725]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2834.0,"contact_point_centroid":[0.44551,-0.04471,0.07292],"force_p95":0.10377,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35567,"mean_force":0.06104,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.44464,-0.02554,0.07103]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2637.0,"contact_point_centroid":[0.44536,-0.00635,0.07339],"force_p95":0.11188,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33471,"mean_force":0.06508,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.44465,-0.02554,0.07085]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":976.0,"contact_point_centroid":[0.62027,0.17409,0.1602],"force_p95":0.17622,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31754,"mean_force":0.10132,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.6148,0.19236,0.16157]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":960.0,"contact_point_centroid":[0.62025,0.21084,0.16029],"force_p95":0.18204,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27041,"mean_force":0.10469,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.61476,0.1923,0.16184]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45856,-0.02617,-0.00205],"force_p95":0.13885,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19185,"mean_force":0.12716,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.44819,-0.0257,0.02718]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6563.0,"contact_point_centroid":[0.53494,0.06579,0.15614],"force_p95":0.10754,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15543,"mean_force":0.07884,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53042,0.08444,0.15459]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6520.0,"contact_point_centroid":[0.53839,0.10739,0.15718],"force_p95":0.11018,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14048,"mean_force":0.07752,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53381,0.08876,0.15566]},{"body_a":"world","body_b":"grasp_target","contact_count":1280.0,"contact_point_centroid":[0.45856,-0.02632,-0.0019],"force_p95":0.13566,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48017,-0.01102,0.24824]},{"body_a":"world","body_b":"grasp_target","contact_count":2640.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45608,-0.02437,0.11314]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5294.0,"contact_point_centroid":[0.44642,-0.00641,0.02771],"force_p95":0.06499,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09667,"mean_force":0.0411,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.44713,-0.02566,0.02617]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5415.0,"contact_point_centroid":[0.44643,-0.04495,0.02746],"force_p95":0.06507,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08233,"mean_force":0.04123,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.44713,-0.02566,0.02618]}],"total_contact_groups":12},"final_pose_error":0.02053,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.63544,0.19914,0.11825],"final_tcp_position":[0.62005,0.19921,0.13619],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"phases":[{"n_steps":321.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.46053,-0.02296,0.19556],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16959,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":660.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_object","tcp_end":[0.45447,-0.02593,0.03318],"tcp_start":[0.46053,-0.02296,0.19556],"tcp_to_object_dist_end":0.00826,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02571,0.0258],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30331,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.4471,-0.02566,0.02615],"tcp_start":[0.45447,-0.02593,0.03318],"tcp_to_object_dist_end":0.01134,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":146.0,"n_steps_budget":600.0,"object_pos_end":[0.4637,-0.02543,0.1267],"object_pos_start":[0.45844,-0.02571,0.0258],"object_to_goal_dist_end":0.28713,"object_to_goal_dist_start":0.30331,"object_z_max":0.12601,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_clearance","tcp_end":[0.44541,-0.02549,0.12928],"tcp_start":[0.4471,-0.02566,0.02615],"tcp_to_object_dist_end":0.01847,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":509.0,"n_steps_budget":1000.0,"object_pos_end":[0.62706,0.18693,0.16681],"object_pos_start":[0.4637,-0.02543,0.1267],"object_to_goal_dist_end":0.05691,"object_to_goal_dist_start":0.28713,"object_z_max":0.16673,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.61167,0.1872,0.18037],"tcp_start":[0.44541,-0.02549,0.12928],"tcp_to_object_dist_end":0.02051,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":97.0,"n_steps_budget":1000.0,"object_pos_end":[0.63544,0.19914,0.11825],"object_pos_start":[0.62706,0.18693,0.16681],"object_to_goal_dist_end":0.0113,"object_to_goal_dist_start":0.05691,"object_z_max":0.16685,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_at_goal","tcp_end":[0.62005,0.19921,0.13619],"tcp_start":[0.61167,0.1872,0.18037],"tcp_to_object_dist_end":0.02363,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.00707,"average_solve_count":283.0,"average_success_count":283.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_offset_z":0.16282,"approach_above.approach_speed":0.18974,"descend_to_grasp.descend_speed":0.0547,"descend_to_grasp.descend_tolerance":0.01053,"lift_up.lift_height":0.12944,"lift_up.lift_speed":0.15209,"lift_up.lift_tolerance":0.04033,"place_at_goal.place_speed":0.02521,"place_at_goal.place_tolerance":0.02189,"place_at_goal.place_z_offset":-0.01441,"transport_to_goal.transport_speed":0.04072,"transport_to_goal.transport_tolerance":0.0379},"optimized_scores":{"best_composite_score":0.25769,"best_fitness_score":0.97769,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":62.0,"contact_point_centroid":[0.53984,0.00072,-0.0015],"force_p95":0.78358,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.80949,"mean_force":0.34844,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.52847,0.00085,0.02575]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2186.0,"contact_point_centroid":[0.5284,-0.01834,0.06695],"force_p95":0.12932,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3758,"mean_force":0.07189,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.52688,0.00081,0.06415]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2442.0,"contact_point_centroid":[0.52851,0.01981,0.065],"force_p95":0.12433,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35297,"mean_force":0.06638,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.52688,0.00081,0.06287]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1136.0,"contact_point_centroid":[0.64007,0.1249,0.22351],"force_p95":0.12691,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2266,"mean_force":0.08915,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.63437,0.14343,0.22261]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1128.0,"contact_point_centroid":[0.63997,0.16185,0.22445],"force_p95":0.13215,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21952,"mean_force":0.0909,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.63422,0.14321,0.22366]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00099,-0.00203],"force_p95":0.13152,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15741,"mean_force":0.12522,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.53144,0.0009,0.02621]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4386.0,"contact_point_centroid":[0.5836,0.0514,0.17966],"force_p95":0.1094,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15127,"mean_force":0.08322,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57866,0.06998,0.17785]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4162.0,"contact_point_centroid":[0.58439,0.08975,0.18093],"force_p95":0.11251,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14739,"mean_force":0.08552,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57952,0.0711,0.17892]},{"body_a":"world","body_b":"grasp_target","contact_count":1436.0,"contact_point_centroid":[0.54431,0.00113,-0.00191],"force_p95":0.13523,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51681,0.00047,0.24841]},{"body_a":"world","body_b":"grasp_target","contact_count":2072.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53605,0.00099,0.11578]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4116.0,"contact_point_centroid":[0.53099,-0.01832,0.02754],"force_p95":0.07608,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1105,"mean_force":0.0517,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.53021,0.00088,0.0248]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4875.0,"contact_point_centroid":[0.53099,0.01996,0.02667],"force_p95":0.06803,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09609,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.53021,0.00088,0.0248]}],"total_contact_groups":12},"final_pose_error":0.02143,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.65821,0.14994,0.1823],"final_tcp_position":[0.63894,0.14992,0.19451],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"phases":[{"n_steps":360.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.53608,0.00097,0.1983],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17247,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":518.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_object","tcp_end":[0.53876,0.00103,0.03474],"tcp_start":[0.53608,0.00097,0.1983],"tcp_to_object_dist_end":0.01033,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54415,0.00074,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25052,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.53018,0.00088,0.02476],"tcp_start":[0.53876,0.00103,0.03474],"tcp_to_object_dist_end":0.01402,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":133.0,"n_steps_budget":600.0,"object_pos_end":[0.54572,0.00069,0.11478],"object_pos_start":[0.54415,0.00074,0.02588],"object_to_goal_dist_end":0.20244,"object_to_goal_dist_start":0.25052,"object_z_max":0.11409,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_clearance","tcp_end":[0.52732,0.00081,0.11462],"tcp_start":[0.53018,0.00088,0.02476],"tcp_to_object_dist_end":0.0184,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":356.0,"n_steps_budget":1000.0,"object_pos_end":[0.64936,0.13822,0.2339],"object_pos_start":[0.54572,0.00069,0.11478],"object_to_goal_dist_end":0.04722,"object_to_goal_dist_start":0.20244,"object_z_max":0.23355,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.63125,0.13826,0.24332],"tcp_start":[0.52732,0.00081,0.11462],"tcp_to_object_dist_end":0.0204,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":101.0,"n_steps_budget":1000.0,"object_pos_end":[0.65821,0.14994,0.1823],"object_pos_start":[0.64936,0.13822,0.2339],"object_to_goal_dist_end":0.01599,"object_to_goal_dist_start":0.04722,"object_z_max":0.23447,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_at_goal","tcp_end":[0.63894,0.14992,0.19451],"tcp_start":[0.63125,0.13826,0.24332],"tcp_to_object_dist_end":0.02281,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```