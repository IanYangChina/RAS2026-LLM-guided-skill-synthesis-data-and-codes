## Search State

- **Seed**: 2
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0212 | 0.40 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0357 | 0.37 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 11 | -0.0578 | 0.27 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 11 | -0.1063 | 0.27 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 11 | -0.0186 | 0.16 | ✅ accepted |

**Proposal policy**: task_score is 0.40 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.021) — your mutation base

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
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: world_z
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.12
      - 0.28
      default: 0.2
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
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
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
- id: descend_to_place
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
  guards:
  - id: grasp_integrity
    when: after_phase
    predicate: object_lifted
    threshold: 0.01
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: place_at_goal
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
    release_timeout:
      type: scalar
      range:
      - 0.2
      - 1.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace

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
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.2, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=object_lifted, when=after_phase, predicate=object_lifted, on_failure=abort, threshold=0.03
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=object_retained, when=after_phase, predicate=object_lifted, on_failure=abort, threshold=0.02
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=grasp_integrity, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.01
  - retries: max_attempts=1, strategy=reduce_speed
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_timeout: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: -0.021
- **task_score** (E): 0.398
- **fitness_score**: 0.679  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.700

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_above | 1.00 | 0.1238 |
| descend_to_grasp | 1.00 | 0.1476 |
| grasp_close | 1.00 | 0.0115 |
| lift_up | 0.67 | 0.1018 |
| transport_to_goal | 1.00 | 0.2574 |
| descend_to_place | 1.00 | 0.0042 |
| release_object | 1.00 | 0.0202 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.491, -0.013, 0.183) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.491, -0.013, 0.183)→(0.488, -0.015, 0.036) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 |
| grasp_close | grasp | 1.00 / step_budget | (0.488, -0.015, 0.036)→(0.480, -0.015, 0.027) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 |
| lift_up | lift | 0.67 / step_budget | (0.480, -0.015, 0.027)→(0.476, -0.015, 0.129) | (0.493, -0.015, 0.026)→(0.490, -0.015, 0.118) | 0.281→0.249 |
| transport_to_goal | approach | 1.00 / step_budget | (0.476, -0.015, 0.129)→(0.620, 0.158, 0.245) | (0.490, -0.015, 0.118)→(0.630, 0.147, 0.054) | 0.249→0.116 |
| descend_to_place | descend | 1.00 / step_budget | (0.625, 0.156, 0.197)→(0.625, 0.156, 0.193) | (0.634, 0.155, 0.099)→(0.635, 0.165, 0.016) | 0.091→0.174 |
| release_object | release | 1.00 / step_budget | (0.625, 0.156, 0.193)→(0.619, 0.154, 0.212) | (0.635, 0.165, 0.016)→(0.635, 0.165, 0.016) | 0.174→0.174 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.565
- phase_score: 0.469
- phase_breakdown.approach_object_score: 0.375
- phase_breakdown.place_at_goal_score: 0.166
- phase_breakdown.grasp_object_score: 1.000
- phase_breakdown.lift_clearance_score: 0.222
- grasp_place_fitness: 0.764

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.764
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.565
- **Median Q (composite search score)**: -0.063
- **K-run variance**: 0.0036
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.365


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.86486,"average_solve_count":333.0,"average_success_count":333.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_offset_z":0.16955,"approach_above.approach_speed":0.05402,"descend_to_grasp.descend_speed":0.05769,"descend_to_grasp.descend_tolerance":0.01262,"descend_to_place.place_speed":0.01847,"descend_to_place.place_tolerance":0.01005,"lift_up.lift_height":0.22407,"lift_up.lift_speed":0.0571,"release_object.release_timeout":0.42425,"transport_to_goal.transport_speed":0.0787,"transport_to_goal.transport_tolerance":0.02738},"optimized_scores":{"best_composite_score":-0.06329,"best_fitness_score":0.63671,"best_task_score":0.31323},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":935.0,"contact_point_centroid":[0.63489,0.16515,-0.0034],"force_p95":0.65411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17858,"mean_force":0.18116,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62087,0.15129,0.22757]},{"body_a":"world","body_b":"grasp_target","contact_count":160.0,"contact_point_centroid":[0.47195,-0.01906,-0.00117],"force_p95":0.43238,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61627,"mean_force":0.09436,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.46277,-0.01957,0.03147]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7152.0,"contact_point_centroid":[0.52319,0.02645,0.1823],"force_p95":0.13515,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30902,"mean_force":0.07278,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51992,0.04519,0.18172]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20210.0,"contact_point_centroid":[0.4602,-0.00034,0.08137],"force_p95":0.07552,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29254,"mean_force":0.05029,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.46025,-0.01949,0.07947]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20184.0,"contact_point_centroid":[0.46027,-0.03863,0.07999],"force_p95":0.07424,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2897,"mean_force":0.05067,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.46026,-0.01949,0.07833]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7119.0,"contact_point_centroid":[0.52476,0.06566,0.18358],"force_p95":0.13408,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22735,"mean_force":0.07342,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52154,0.0469,0.18318]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02004,-0.00205],"force_p95":0.13771,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18693,"mean_force":0.12673,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.4654,-0.01963,0.03098]},{"body_a":"world","body_b":"grasp_target","contact_count":1204.0,"contact_point_centroid":[0.47616,-0.02015,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48791,-0.00816,0.25507]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.63479,0.16496,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62088,0.15479,0.19255]},{"body_a":"world","body_b":"grasp_target","contact_count":1988.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47298,-0.01842,0.12286]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5070.0,"contact_point_centroid":[0.4638,-0.00035,0.03259],"force_p95":0.06603,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09554,"mean_force":0.04291,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.46431,-0.0196,0.02991]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5398.0,"contact_point_centroid":[0.46369,-0.03886,0.032],"force_p95":0.06505,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08668,"mean_force":0.04118,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.46431,-0.0196,0.02991]},{"body_a":"left_finger","body_b":"right_finger","contact_count":823.0,"contact_point_centroid":[0.62189,0.15207,0.22372],"force_p95":0.01277,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01618,"mean_force":0.01082,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62156,0.15205,0.22128]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.62373,0.15558,0.19134],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01098,"mean_force":0.01006,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62341,0.15556,0.18903]}],"total_contact_groups":14},"final_pose_error":0.00772,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.63479,0.16496,0.01602],"final_tcp_position":[0.62492,0.15592,0.1926],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"phases":[{"n_steps":302.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.47645,-0.01717,0.20886],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18287,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":497.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_object","tcp_end":[0.47202,-0.01978,0.03766],"tcp_start":[0.47645,-0.01717,0.20886],"tcp_to_object_dist_end":0.01236,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47604,-0.01964,0.02581],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28825,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.46428,-0.0196,0.02988],"tcp_start":[0.47202,-0.01978,0.03766],"tcp_to_object_dist_end":0.01244,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47207,-0.01944,0.11654],"object_pos_start":[0.47604,-0.01964,0.02581],"object_to_goal_dist_end":0.2504,"object_to_goal_dist_start":0.28825,"object_z_max":0.11647,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_clearance","tcp_end":[0.46027,-0.01948,0.12818],"tcp_start":[0.46428,-0.0196,0.02988],"tcp_to_object_dist_end":0.01658,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":609.0,"n_steps_budget":1000.0,"object_pos_end":[0.63368,0.15549,0.09919],"object_pos_start":[0.47207,-0.01944,0.11654],"object_to_goal_dist_end":0.09093,"object_to_goal_dist_start":0.2504,"object_z_max":0.22871,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.61728,0.14622,0.2705],"tcp_start":[0.46027,-0.01948,0.12818],"tcp_to_object_dist_end":0.17234,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":257.0,"n_steps_budget":1000.0,"object_pos_end":[0.63479,0.16496,0.01602],"object_pos_start":[0.63368,0.15549,0.09919],"object_to_goal_dist_end":0.17412,"object_to_goal_dist_start":0.09093,"object_z_max":0.09919,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"place_at_goal","tcp_end":[0.62492,0.15592,0.1926],"tcp_start":[0.62529,0.15571,0.19682],"tcp_to_object_dist_end":0.17709,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63479,0.16496,0.01602],"object_pos_start":[0.63479,0.16496,0.01602],"object_to_goal_dist_end":0.17412,"object_to_goal_dist_start":0.17412,"object_z_max":0.01602,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.61941,0.15433,0.21197],"tcp_start":[0.62492,0.15592,0.1926],"tcp_to_object_dist_end":0.19684,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30846,"average_solve_count":201.0,"average_success_count":201.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_offset_z":0.15977,"approach_above.approach_speed":0.13829,"descend_to_grasp.descend_speed":0.064,"descend_to_grasp.descend_tolerance":0.00905,"descend_to_place.place_speed":0.0323,"descend_to_place.place_tolerance":0.01121,"lift_up.lift_height":0.12224,"lift_up.lift_speed":0.17446,"release_object.release_timeout":0.28503,"transport_to_goal.transport_speed":0.05945,"transport_to_goal.transport_tolerance":0.03323},"optimized_scores":{"best_composite_score":0.0641,"best_fitness_score":0.7641,"best_task_score":0.56478},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":134.0,"contact_point_centroid":[0.45616,-0.02533,-0.00116],"force_p95":0.54841,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72927,"mean_force":0.10251,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.44582,-0.0256,0.02861]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4143.0,"contact_point_centroid":[0.51314,0.03959,0.15768],"force_p95":0.1515,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30841,"mean_force":0.09926,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50822,0.05773,0.15929]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8676.0,"contact_point_centroid":[0.44529,-0.00653,0.07557],"force_p95":0.10346,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2965,"mean_force":0.06365,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.44355,-0.02549,0.07342]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9086.0,"contact_point_centroid":[0.44532,-0.04446,0.07435],"force_p95":0.10208,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28224,"mean_force":0.06152,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.44354,-0.02549,0.07257]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3587.0,"contact_point_centroid":[0.51443,0.07783,0.15843],"force_p95":0.16893,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22455,"mean_force":0.10543,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50968,0.05958,0.15986]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45856,-0.02617,-0.00205],"force_p95":0.13922,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19237,"mean_force":0.12725,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.44818,-0.02568,0.02789]},{"body_a":"world","body_b":"grasp_target","contact_count":1252.0,"contact_point_centroid":[0.45856,-0.02632,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48027,-0.01097,0.24988]},{"body_a":"world","body_b":"grasp_target","contact_count":2432.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45626,-0.02433,0.11542]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5294.0,"contact_point_centroid":[0.44642,-0.0064,0.02844],"force_p95":0.06506,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0974,"mean_force":0.0411,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.44712,-0.02564,0.02689]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5416.0,"contact_point_centroid":[0.44642,-0.04493,0.02819],"force_p95":0.06514,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08205,"mean_force":0.04123,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.44712,-0.02564,0.02689]}],"total_contact_groups":10},"final_pose_error":0.03278,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61999,0.16848,0.03887],"final_tcp_position":[0.61105,0.18624,0.19903],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"phases":[{"n_steps":314.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.46067,-0.02289,0.19882],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17285,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":608.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_object","tcp_end":[0.4545,-0.02591,0.03395],"tcp_start":[0.46067,-0.02289,0.19882],"tcp_to_object_dist_end":0.00892,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.0257,0.0258],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.3033,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.44709,-0.02564,0.02686],"tcp_start":[0.4545,-0.02591,0.03395],"tcp_to_object_dist_end":0.0114,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":538.0,"n_steps_budget":600.0,"object_pos_end":[0.46215,-0.02542,0.12578],"object_pos_start":[0.45844,-0.0257,0.0258],"object_to_goal_dist_end":0.28799,"object_to_goal_dist_start":0.3033,"object_z_max":0.12565,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_clearance","tcp_end":[0.44354,-0.02547,0.13623],"tcp_start":[0.44709,-0.02564,0.02686],"tcp_to_object_dist_end":0.02135,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":487.0,"n_steps_budget":1000.0,"object_pos_end":[0.61999,0.16848,0.03887],"object_pos_start":[0.46215,-0.02542,0.12578],"object_to_goal_dist_end":0.0857,"object_to_goal_dist_start":0.28799,"object_z_max":0.16374,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.61105,0.18624,0.19903],"tcp_start":[0.44354,-0.02547,0.13623],"tcp_to_object_dist_end":0.16139,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.35323,"average_solve_count":201.0,"average_success_count":201.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_offset_z":0.10516,"approach_above.approach_speed":0.06196,"descend_to_grasp.descend_speed":0.05089,"descend_to_grasp.descend_tolerance":0.01119,"descend_to_place.place_speed":0.02315,"descend_to_place.place_tolerance":0.01653,"lift_up.lift_height":0.12222,"lift_up.lift_speed":0.05964,"release_object.release_timeout":0.91034,"transport_to_goal.transport_speed":0.09103,"transport_to_goal.transport_tolerance":0.03559},"optimized_scores":{"best_composite_score":-0.06444,"best_fitness_score":0.63556,"best_task_score":0.31643},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":5.0,"contact_point_centroid":[0.64087,0.10427,-0.00201],"force_p95":1.75585,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.75862,"mean_force":1.51645,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.63229,0.14015,0.26382]},{"body_a":"world","body_b":"grasp_target","contact_count":199.0,"contact_point_centroid":[0.53955,0.00062,-0.00113],"force_p95":0.46574,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6991,"mean_force":0.10754,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.52798,0.00084,0.02694]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3768.0,"contact_point_centroid":[0.56028,0.02508,0.1631],"force_p95":0.17509,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34473,"mean_force":0.08325,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55665,0.04358,0.16361]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18914.0,"contact_point_centroid":[0.52627,-0.0183,0.07673],"force_p95":0.07775,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3287,"mean_force":0.05401,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.52547,0.0008,0.0749]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19284.0,"contact_point_centroid":[0.52628,0.01989,0.07576],"force_p95":0.07739,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31326,"mean_force":0.05325,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.52549,0.0008,0.07404]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3089.0,"contact_point_centroid":[0.55992,0.06192,0.16314],"force_p95":0.17588,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27662,"mean_force":0.09204,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55628,0.04309,0.16312]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00099,-0.00203],"force_p95":0.13158,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15739,"mean_force":0.12522,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.53117,0.0009,0.0268]},{"body_a":"world","body_b":"grasp_target","contact_count":2272.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51711,0.00049,0.22003]},{"body_a":"world","body_b":"grasp_target","contact_count":1312.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53631,0.001,0.08832]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4116.0,"contact_point_centroid":[0.53082,-0.01832,0.02813],"force_p95":0.07609,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11109,"mean_force":0.05171,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.52995,0.00088,0.02539]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4875.0,"contact_point_centroid":[0.53081,0.01995,0.02726],"force_p95":0.06805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09608,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.52995,0.00088,0.02539]}],"total_contact_groups":11},"final_pose_error":0.03505,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.63562,0.11711,0.02387],"final_tcp_position":[0.63279,0.14078,0.26447],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"phases":[{"n_steps":569.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.53693,0.00099,0.14185],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11607,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":328.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"grasp_object","tcp_end":[0.53853,0.00103,0.03536],"tcp_start":[0.53693,0.00099,0.14185],"tcp_to_object_dist_end":0.01098,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54416,0.00074,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25052,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","tcp_end":[0.52991,0.00087,0.02535],"tcp_start":[0.53853,0.00103,0.03536],"tcp_to_object_dist_end":0.01425,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53651,0.00082,0.11274],"object_pos_start":[0.54416,0.00074,0.02588],"object_to_goal_dist_end":0.2079,"object_to_goal_dist_start":0.25052,"object_z_max":0.11263,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"lift_clearance","tcp_end":[0.5256,0.00081,0.12282],"tcp_start":[0.52991,0.00087,0.02535],"tcp_to_object_dist_end":0.01485,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":388.0,"n_steps_budget":1000.0,"object_pos_end":[0.63562,0.11711,0.02387],"object_pos_start":[0.53651,0.00082,0.11274],"object_to_goal_dist_end":0.1726,"object_to_goal_dist_start":0.2079,"object_z_max":0.20285,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"place_at_goal","tcp_end":[0.63279,0.14078,0.26447],"tcp_start":[0.5256,0.00081,0.12282],"tcp_to_object_dist_end":0.24178,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```