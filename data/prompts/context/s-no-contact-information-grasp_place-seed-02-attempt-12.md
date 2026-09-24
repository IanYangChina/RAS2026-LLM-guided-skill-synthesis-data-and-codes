## Search State

- **Seed**: 2
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.1950 | 0.94 | ✅ accepted |
| 11 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | force_threshold_switch | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 11 | 0.0195 | 0.39 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.1713 | 0.73 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 13 | -0.1364 | 0.37 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0212 | 0.40 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.94). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.938, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.195) — your mutation base

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
      - 0.005
      - 0.02
      default: 0.008
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
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
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
      - 0.04
      default: 0.015
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
      - 0.005
      - 0.02
      default: 0.008
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

- **Composite score**: 0.195
- **task_score** (E): 0.938
- **fitness_score**: 0.865  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.670

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_above | 1.00 | 0.1088 |
| descend_to_grasp | 1.00 | 0.1611 |
| grasp_close | 1.00 | 0.0116 |
| lift_up | 0.67 | 0.0988 |
| transport_to_goal | 1.00 | 0.2491 |
| place_at_goal | 1.00 | 0.0405 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.490, -0.013, 0.199) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.490, -0.013, 0.199)→(0.488, -0.015, 0.038) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 |
| grasp_close | grasp | 1.00 / step_budget | (0.488, -0.015, 0.038)→(0.480, -0.015, 0.029) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 |
| lift_up | lift | 0.67 / step_budget | (0.480, -0.015, 0.029)→(0.477, -0.015, 0.128) | (0.493, -0.015, 0.026)→(0.491, -0.015, 0.116) | 0.281→0.249 |
| transport_to_goal | approach | 1.00 / step_budget | (0.477, -0.015, 0.128)→(0.620, 0.158, 0.225) | (0.491, -0.015, 0.116)→(0.628, 0.158, 0.205) | 0.249→0.044 |
| place_at_goal | descend | 1.00 / step_budget | (0.620, 0.158, 0.225)→(0.627, 0.168, 0.187) | (0.628, 0.158, 0.205)→(0.635, 0.166, 0.156) | 0.044→0.017 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.521
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.688
- phase_breakdown.approach_object_score: 0.666
- phase_breakdown.place_at_goal_score: 0.711
- phase_breakdown.grasp_object_score: 1.000
- phase_breakdown.lift_clearance_score: 0.206
- grasp_place_fitness: 0.982

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.982
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.310
- **K-run variance**: 0.0267
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.339


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23144,"average_solve_count":229.0,"average_success_count":229.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_offset_z":0.16292,"approach_above.approach_speed":0.17874,"descend_to_grasp.descend_speed":0.10617,"descend_to_grasp.descend_tolerance":0.01356,"lift_up.lift_height":0.1144,"lift_up.lift_speed":0.15498,"place_at_goal.place_speed":0.0293,"place_at_goal.place_tolerance":0.0196,"place_at_goal.place_z_offset":0.01894,"transport_to_goal.transport_speed":0.03655,"transport_to_goal.transport_tolerance":0.03316},"optimized_scores":{"best_composite_score":0.30955,"best_fitness_score":0.97955,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":136.0,"contact_point_centroid":[0.47331,-0.01954,-0.00123],"force_p95":0.44384,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66986,"mean_force":0.09694,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.46302,-0.01956,0.03263]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8501.0,"contact_point_centroid":[0.46255,-0.00052,0.07676],"force_p95":0.1032,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33352,"mean_force":0.06446,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.46069,-0.01949,0.07456]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8948.0,"contact_point_centroid":[0.46257,-0.03843,0.07536],"force_p95":0.10188,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31405,"mean_force":0.06194,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.46069,-0.01949,0.07356]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":521.0,"contact_point_centroid":[0.62163,0.12769,0.23437],"force_p95":0.15073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29786,"mean_force":0.10757,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.61645,0.14548,0.23855]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":412.0,"contact_point_centroid":[0.62183,0.16329,0.23573],"force_p95":0.21586,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29417,"mean_force":0.14647,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.61612,0.14512,0.23982]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02005,-0.00205],"force_p95":0.13807,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18735,"mean_force":0.12683,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.46548,-0.01962,0.03215]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4254.0,"contact_point_centroid":[0.53689,0.07484,0.18594],"force_p95":0.13901,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17885,"mean_force":0.10054,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53141,0.05636,0.1859]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5118.0,"contact_point_centroid":[0.53548,0.03679,0.18469],"force_p95":0.13047,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17781,"mean_force":0.08653,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53022,0.05512,0.18499]},{"body_a":"world","body_b":"grasp_target","contact_count":1168.0,"contact_point_centroid":[0.47616,-0.02015,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48779,-0.00829,0.25171]},{"body_a":"world","body_b":"grasp_target","contact_count":1676.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47309,-0.01849,0.12045]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4924.0,"contact_point_centroid":[0.46409,-0.00037,0.03354],"force_p95":0.06755,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09612,"mean_force":0.04404,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.4644,-0.01959,0.03108]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5155.0,"contact_point_centroid":[0.46413,-0.03882,0.03299],"force_p95":0.06682,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08628,"mean_force":0.04298,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.4644,-0.01959,0.03108]}],"total_contact_groups":12},"final_pose_error":0.01925,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62995,0.14966,0.19673],"final_tcp_position":[0.62097,0.15041,0.22253],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"phases":[{"n_steps":293.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.47624,-0.01734,0.20229],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17629,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":419.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_object","tcp_end":[0.47213,-0.01977,0.0389],"tcp_start":[0.47624,-0.01734,0.20229],"tcp_to_object_dist_end":0.0135,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47604,-0.01964,0.02581],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28825,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.46437,-0.01959,0.03105],"tcp_start":[0.47213,-0.01977,0.0389],"tcp_to_object_dist_end":0.0128,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":534.0,"n_steps_budget":600.0,"object_pos_end":[0.47792,-0.0194,0.1188],"object_pos_start":[0.47604,-0.01964,0.02581],"object_to_goal_dist_end":0.24603,"object_to_goal_dist_start":0.28825,"object_z_max":0.11867,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_clearance","tcp_end":[0.46066,-0.01947,0.13285],"tcp_start":[0.46437,-0.01959,0.03105],"tcp_to_object_dist_end":0.02226,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":463.0,"n_steps_budget":1000.0,"object_pos_end":[0.62094,0.14141,0.22576],"object_pos_start":[0.47792,-0.0194,0.1188],"object_to_goal_dist_end":0.04128,"object_to_goal_dist_start":0.24603,"object_z_max":0.22552,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.6134,0.14167,0.24898],"tcp_start":[0.46066,-0.01947,0.13285],"tcp_to_object_dist_end":0.02442,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":67.0,"n_steps_budget":1000.0,"object_pos_end":[0.62995,0.14966,0.19673],"object_pos_start":[0.62094,0.14141,0.22576],"object_to_goal_dist_end":0.01175,"object_to_goal_dist_start":0.04128,"object_z_max":0.226,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_at_goal","tcp_end":[0.62097,0.15041,0.22253],"tcp_start":[0.6134,0.14167,0.24898],"tcp_to_object_dist_end":0.02733,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42105,"average_solve_count":209.0,"average_success_count":209.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_offset_z":0.13068,"approach_above.approach_speed":0.29613,"descend_to_grasp.descend_speed":0.06755,"descend_to_grasp.descend_tolerance":0.00922,"lift_up.lift_height":0.18699,"lift_up.lift_speed":0.0505,"place_at_goal.place_speed":0.02566,"place_at_goal.place_tolerance":0.00665,"place_at_goal.place_z_offset":0.0114,"transport_to_goal.transport_speed":0.1073,"transport_to_goal.transport_tolerance":0.0239},"optimized_scores":{"best_composite_score":0.31156,"best_fitness_score":0.98156,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":149.0,"contact_point_centroid":[0.45521,-0.02525,-0.00117],"force_p95":0.4952,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66436,"mean_force":0.10822,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.44562,-0.02559,0.02862]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20461.0,"contact_point_centroid":[0.44295,-0.04463,0.08105],"force_p95":0.07175,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27523,"mean_force":0.04987,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.44314,-0.02548,0.07933]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20439.0,"contact_point_centroid":[0.443,-0.00633,0.0825],"force_p95":0.07106,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26735,"mean_force":0.04956,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.44315,-0.02548,0.08047]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18382.0,"contact_point_centroid":[0.62133,0.21891,0.1419],"force_p95":0.07711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19875,"mean_force":0.05222,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.61984,0.20021,0.14196]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45856,-0.02617,-0.00205],"force_p95":0.13935,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1924,"mean_force":0.12726,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.4481,-0.02568,0.02805]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13351.0,"contact_point_centroid":[0.62109,0.18123,0.14071],"force_p95":0.10095,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17733,"mean_force":0.07025,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.61994,0.20033,0.1414]},{"body_a":"world","body_b":"grasp_target","contact_count":1472.0,"contact_point_centroid":[0.45856,-0.02632,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.47942,-0.0114,0.23526]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10922.0,"contact_point_centroid":[0.52551,0.06175,0.15603],"force_p95":0.09277,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12814,"mean_force":0.06386,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52578,0.08096,0.155]},{"body_a":"world","body_b":"grasp_target","contact_count":1984.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4556,-0.02463,0.10137]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14220.0,"contact_point_centroid":[0.52767,0.10179,0.15645],"force_p95":0.07461,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11947,"mean_force":0.04957,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52734,0.08292,0.15547]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5294.0,"contact_point_centroid":[0.44635,-0.00639,0.02877],"force_p95":0.06508,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09741,"mean_force":0.04111,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.44704,-0.02564,0.02705]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5416.0,"contact_point_centroid":[0.44635,-0.04493,0.02852],"force_p95":0.06526,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0821,"mean_force":0.04123,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.44704,-0.02564,0.02705]}],"total_contact_groups":12},"final_pose_error":0.00942,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62595,0.20377,0.10674],"final_tcp_position":[0.62266,0.20341,0.12867],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"phases":[{"n_steps":369.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.45944,-0.02349,0.17007],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14408,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":496.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_object","tcp_end":[0.4544,-0.02591,0.0341],"tcp_start":[0.45944,-0.02349,0.17007],"tcp_to_object_dist_end":0.00909,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.0257,0.0258],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.3033,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.44701,-0.02564,0.02702],"tcp_start":[0.4544,-0.02591,0.0341],"tcp_to_object_dist_end":0.0115,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45231,-0.0254,0.1234],"object_pos_start":[0.45844,-0.0257,0.0258],"object_to_goal_dist_end":0.29374,"object_to_goal_dist_start":0.3033,"object_z_max":0.12332,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_clearance","tcp_end":[0.44322,-0.02547,0.13244],"tcp_start":[0.44701,-0.02564,0.02702],"tcp_to_object_dist_end":0.01282,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":687.0,"n_steps_budget":1000.0,"object_pos_end":[0.62327,0.19285,0.16623],"object_pos_start":[0.45231,-0.0254,0.1234],"object_to_goal_dist_end":0.05476,"object_to_goal_dist_start":0.29374,"object_z_max":0.16619,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.61591,0.1931,0.18229],"tcp_start":[0.44322,-0.02547,0.13244],"tcp_to_object_dist_end":0.01768,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62595,0.20377,0.10674],"object_pos_start":[0.62327,0.19285,0.16623],"object_to_goal_dist_end":0.00957,"object_to_goal_dist_start":0.05476,"object_z_max":0.16623,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_at_goal","tcp_end":[0.62266,0.20341,0.12867],"tcp_start":[0.61591,0.1931,0.18229],"tcp_to_object_dist_end":0.02217,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.93878,"average_solve_count":294.0,"average_success_count":294.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_offset_z":0.18988,"approach_above.approach_speed":0.0719,"descend_to_grasp.descend_speed":0.05593,"descend_to_grasp.descend_tolerance":0.01541,"lift_up.lift_height":0.10201,"lift_up.lift_speed":0.13048,"place_at_goal.place_speed":0.01907,"place_at_goal.place_tolerance":0.01485,"place_at_goal.place_z_offset":0.00925,"transport_to_goal.transport_speed":0.0336,"transport_to_goal.transport_tolerance":0.03768},"optimized_scores":{"best_composite_score":-0.03605,"best_fitness_score":0.63395,"best_task_score":0.81459},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":155.0,"contact_point_centroid":[0.54046,0.00062,-0.00123],"force_p95":0.37951,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63276,"mean_force":0.09304,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.52842,0.00084,0.03151]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7469.0,"contact_point_centroid":[0.52909,-0.01803,0.06949],"force_p95":0.10886,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33746,"mean_force":0.07254,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.5259,0.00081,0.06757]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7800.0,"contact_point_centroid":[0.52897,0.01963,0.06897],"force_p95":0.10648,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3196,"mean_force":0.06997,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.52595,0.00081,0.06694]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":534.0,"contact_point_centroid":[0.63805,0.15977,0.23073],"force_p95":0.21324,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30288,"mean_force":0.12969,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.63291,0.14167,0.23541]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":669.0,"contact_point_centroid":[0.63848,0.125,0.22766],"force_p95":0.14659,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30165,"mean_force":0.10071,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.63353,0.1426,0.23219]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4148.0,"contact_point_centroid":[0.57583,0.04357,0.17114],"force_p95":0.13469,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18227,"mean_force":0.08404,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5714,0.06189,0.17244]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3448.0,"contact_point_centroid":[0.58059,0.0859,0.1768],"force_p95":0.14988,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18015,"mean_force":0.09757,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57578,0.0675,0.17768]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.001,-0.00203],"force_p95":0.13174,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15126,"mean_force":0.12523,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.53133,0.0009,0.03154]},{"body_a":"world","body_b":"grasp_target","contact_count":1240.0,"contact_point_centroid":[0.54431,0.00113,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51643,0.00046,0.26116]},{"body_a":"world","body_b":"grasp_target","contact_count":1752.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53594,0.00098,0.13244]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4117.0,"contact_point_centroid":[0.53094,-0.01832,0.03288],"force_p95":0.07616,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10059,"mean_force":0.05172,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.53012,0.00088,0.03014]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4872.0,"contact_point_centroid":[0.53093,0.01995,0.03201],"force_p95":0.06816,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0953,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.53012,0.00088,0.03014]}],"total_contact_groups":12},"final_pose_error":0.01474,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64806,0.14454,0.16349],"final_tcp_position":[0.63884,0.15009,0.20908],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"phases":[{"n_steps":311.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.53539,0.00095,0.22401],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19819,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":438.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_object","tcp_end":[0.53881,0.00103,0.04039],"tcp_start":[0.53539,0.00095,0.22401],"tcp_to_object_dist_end":0.01539,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54417,0.00075,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25051,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.53009,0.00088,0.0301],"tcp_start":[0.53881,0.00103,0.04039],"tcp_to_object_dist_end":0.01471,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":528.0,"n_steps_budget":600.0,"object_pos_end":[0.54267,0.00088,0.1054],"object_pos_start":[0.54417,0.00075,0.02588],"object_to_goal_dist_end":0.20754,"object_to_goal_dist_start":0.25051,"object_z_max":0.10528,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_clearance","tcp_end":[0.52587,0.00082,0.11902],"tcp_start":[0.53009,0.00088,0.0301],"tcp_to_object_dist_end":0.02163,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":358.0,"n_steps_budget":1000.0,"object_pos_end":[0.64026,0.13834,0.22204],"object_pos_start":[0.54267,0.00088,0.1054],"object_to_goal_dist_end":0.03743,"object_to_goal_dist_start":0.20754,"object_z_max":0.2217,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.63129,0.13852,0.24412],"tcp_start":[0.52587,0.00082,0.11902],"tcp_to_object_dist_end":0.02384,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":104.0,"n_steps_budget":1000.0,"object_pos_end":[0.64806,0.14454,0.16349],"object_pos_start":[0.64026,0.13834,0.22204],"object_to_goal_dist_end":0.03076,"object_to_goal_dist_start":0.03743,"object_z_max":0.22257,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_at_goal","tcp_end":[0.63884,0.15009,0.20908],"tcp_start":[0.63129,0.13852,0.24412],"tcp_to_object_dist_end":0.04684,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```