## Search State

- **Seed**: 3
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2065 | 0.32 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.1555 | 0.21 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.0838 | 0.26 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.0686 | 0.23 | ✅ accepted |
| 2 | rotate → retract → descend → pull → rotate | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.0374 | 0.17 | ❌ rejected |

**Proposal policy**: task_score is 0.32 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`
- Frozen object start: [0.6301274465206397, 0.20821620360643678, 0.11411929633605987]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5, 0.0, 0.3)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.6301274465206397, 0.20821620360643678, 0.11411929633605987)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.45856491671436245, -0.02631894934039003, 0.03)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.45856491671436245, -0.02631894934039003, 0.03]
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
  frozen_object_start: [0.4586, -0.0263, 0.03]
  frozen_task_target: [0.6301, 0.2082, 0.1141]
  frozen_object_starts: {'grasp_target': [0.6301274465206397, 0.20821620360643678, 0.11411929633605987]}
  frozen_targets: {'place_target': [0.5, 0.0, 0.3]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7

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
| `object` | offset from object initial position (0.6301274465206397, 0.20821620360643678, 0.11411929633605987) | approach/contact targets near object start |
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

## Current Skill (Q=0.206) — your mutation base

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
  weight: 0.3
- id: place_at_goal
  target_entity: object
  weight: 0.7
phases:
- id: approach_object
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: body
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.12
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: descend_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: body
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_guard
    when: during_phase
    predicate: force_below
    threshold: 20.0
    on_failure: abort
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
  - id: bilateral_grasp_guard
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
- id: lift_object
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
    - 0.2
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: object_lift_guard
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.02
- id: approach_place
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
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
  parameters:
    approach_place_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 20.0
    on_failure: abort
  subtask_id: place_at_goal
- id: lower_to_place
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
    - 0.005
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
  parameters:
    place_z_offset:
      type: scalar
      range:
      - -0.01
      - 0.02
      default: 0.005
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: place_force_limit
    when: during_phase
    predicate: force_below
    threshold: 20.0
    on_failure: abort
- id: release_object
  type: release
  control: position_control
  termination: pose_tolerance
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
- id: retract_after_place
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
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

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=body, entity=grasp_target, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=body, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=20.0
- **grasp_close** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=bilateral_grasp_guard, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=1, strategy=repeat
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=object_lift_guard, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.02]
- **approach_place** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z
  - parameter_bindings:
    - approach_place_height: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=abort, threshold=20.0
- **lower_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.005], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=place_force_limit, when=during_phase, predicate=force_below, on_failure=abort, threshold=20.0
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract_after_place** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.206
- **task_score** (E): 0.316
- **fitness_score**: 0.636  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1301 |
| descend_grasp | 1.00 | 1.00 | 0.1427 |
| grasp_close | 1.00 | 1.00 | 0.0122 |
| lift_object | 1.00 | 1.00 | 0.1297 |
| approach_place | 0.00 | 1.00 | 0.1733 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.001, 0.177) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.506, 0.001, 0.177)→(0.506, 0.002, 0.034) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 8.607 | 0.123 |
| grasp_close | grasp | 1.00 / step_budget | (0.506, 0.002, 0.034)→(0.498, 0.002, 0.025) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 42.333 | 0.138 | 0.197 |
| lift_object | lift | 1.00 / step_budget | (0.498, 0.002, 0.025)→(0.494, 0.002, 0.155) | (0.511, 0.002, 0.026)→(0.514, 0.002, 0.148) | 0.246→0.216 | 1.00 / 23.000 | 0.113 | 0.715 |
| approach_place | approach | 0.00 / guard_failure | (0.494, 0.002, 0.155)→(0.576, 0.031, 0.009) | (0.514, 0.002, 0.148)→(0.632, 0.062, 0.018) | 0.216→0.193 | 1.00 / 11.667 | 55989.574 | 37.940 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.540
- phase_score: 0.176
- phase_breakdown.place_at_goal_score: 0.068
- phase_breakdown.reach_object_score: 0.427
- grasp_place_fitness: 0.748

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.748
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.540
- **Median Q (composite search score)**: 0.171
- **K-run variance**: 0.0065
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.326


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a4a71a7b2980790489e8194d1356bdee33fb951291c2e0792659ad3d3b3dc711`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `8a78b0f0015ebaf8c4b14c8fbc8142d9b66e4b4efca10f362859101c0ae207df`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.63013,0.20822,0.11412]},{"name":"goal","value":[0.45856,-0.02632,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41892,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.1089,"approach_place.approach_place_height":0.17409,"descend_grasp.descend_speed":0.03009,"lift_object.lift_height":0.11712,"lower_to_place.place_z_offset":0.00274},"optimized_scores":{"best_composite_score":0.13012,"best_fitness_score":0.56012,"best_task_score":0.15848},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"right_finger","contact_count":4.0,"contact_point_centroid":[0.53725,-0.01297,-0.00048],"force_p95":31.39122,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":31.39193,"mean_force":31.04231,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.53683,-0.03567,0.0098]},{"body_a":"world","body_b":"left_finger","contact_count":2.0,"contact_point_centroid":[0.54163,-0.05529,-2e-05],"force_p95":15.18949,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":15.19094,"mean_force":15.17641,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.53683,-0.03567,0.0098]},{"body_a":"world","body_b":"grasp_target","contact_count":24.0,"contact_point_centroid":[0.55808,-0.0357,-0.00738],"force_p95":3.58779,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.87388,"mean_force":3.09612,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.539,-0.03595,0.02289]},{"body_a":"grasp_target","body_b":"hand","contact_count":1.0,"contact_point_centroid":[0.56976,-0.01375,0.03264],"force_p95":2.65665,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.65665,"mean_force":2.65665,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.53683,-0.03567,0.0098]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":779.0,"contact_point_centroid":[0.50261,-0.05018,0.09619],"force_p95":0.58659,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.48628,"mean_force":0.19874,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.49591,-0.03201,0.09582]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":657.0,"contact_point_centroid":[0.49663,-0.01206,0.10175],"force_p95":0.4176,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.29387,"mean_force":0.18879,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.49221,-0.03167,0.10111]},{"body_a":"world","body_b":"grasp_target","contact_count":70.0,"contact_point_centroid":[0.45553,-0.02534,-0.00138],"force_p95":0.63484,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6574,"mean_force":0.16099,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44556,-0.02558,0.02914]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5117.0,"contact_point_centroid":[0.44448,-0.00636,0.07542],"force_p95":0.09903,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30157,"mean_force":0.06052,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44338,-0.02548,0.0729]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5631.0,"contact_point_centroid":[0.44451,-0.04451,0.0743],"force_p95":0.09363,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2921,"mean_force":0.05609,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44336,-0.02548,0.07257]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02616,-0.00206],"force_p95":0.14014,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19287,"mean_force":0.12741,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.44779,-0.02566,0.02885]},{"body_a":"world","body_b":"grasp_target","contact_count":1852.0,"contact_point_centroid":[0.45856,-0.02632,-0.00192],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47894,-0.01162,0.22437]},{"body_a":"world","body_b":"grasp_target","contact_count":1656.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.45508,-0.0248,0.09145]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4815.0,"contact_point_centroid":[0.44674,-0.00641,0.03022],"force_p95":0.06809,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09791,"mean_force":0.04488,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.44671,-0.02562,0.02784]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5172.0,"contact_point_centroid":[0.44659,-0.04485,0.02971],"force_p95":0.06692,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08243,"mean_force":0.043,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.44671,-0.02562,0.02784]}],"total_contact_groups":14},"final_pose_error":0.38532,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.56354,-0.03461,0.0003],"final_tcp_position":[0.53575,-0.03554,0.00511],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":464.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1852.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45869,-0.02387,0.1483],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12231,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":414.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1656.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45428,-0.02589,0.03504],"tcp_start":[0.45869,-0.02387,0.1483],"tcp_to_object_dist_end":0.00999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02566,0.02579],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30327,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13738,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11787.0,"raw_peak_contact_force":0.19287,"tcp_end":[0.44668,-0.02561,0.02781],"tcp_start":[0.45428,-0.02589,0.03504],"tcp_to_object_dist_end":0.01193,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":292.0,"n_steps_budget":750.0,"object_pos_end":[0.46083,-0.02534,0.12051],"object_pos_start":[0.45844,-0.02566,0.02579],"object_to_goal_dist_end":0.28853,"object_to_goal_dist_start":0.30327,"object_z_max":0.12023,"peak_contact_force":0.10844,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10818.0,"raw_peak_contact_force":0.6574,"tcp_end":[0.44313,-0.02545,0.12531],"tcp_start":[0.44668,-0.02561,0.02781],"tcp_to_object_dist_end":0.01834,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":65.0,"n_steps_budget":1000.0,"object_pos_end":[0.56354,-0.03461,0.0003],"object_pos_start":[0.46083,-0.02534,0.12051],"object_to_goal_dist_end":0.27632,"object_to_goal_dist_start":0.28853,"object_z_max":0.12109,"peak_contact_force":167951.73011,"phase_name":"approach_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1467.0,"raw_peak_contact_force":31.39193,"subtask_id":"place_at_goal","tcp_end":[0.53575,-0.03554,0.00511],"tcp_start":[0.44313,-0.02545,0.12531],"tcp_to_object_dist_end":0.02821,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `aa6ec658384c70fac6b4eb656cc8c53536c3d5c760368ab2b384dccf294e2c48`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.64762,0.15808,0.1911]},{"name":"goal","value":[0.54431,0.00113,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.60135,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.15546,"approach_place.approach_place_height":0.21897,"descend_grasp.descend_speed":0.04129,"lift_object.lift_height":0.16812,"lower_to_place.place_z_offset":-0.00729},"optimized_scores":{"best_composite_score":0.17142,"best_fitness_score":0.60142,"best_task_score":0.24839},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"right_finger","contact_count":1.0,"contact_point_centroid":[0.60971,0.05732,-0.00023],"force_p95":34.7874,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":34.7874,"mean_force":34.7874,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.60635,0.04107,0.01583]},{"body_a":"world","body_b":"grasp_target","contact_count":6.0,"contact_point_centroid":[0.67795,0.03709,-0.0032],"force_p95":3.69579,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.7473,"mean_force":2.76108,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.60892,0.0408,0.02138]},{"body_a":"grasp_target","body_b":"hand","contact_count":18.0,"contact_point_centroid":[0.65499,0.04067,0.08797],"force_p95":1.46234,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.72813,"mean_force":0.90221,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.62115,0.03916,0.0582]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.54128,0.00072,-0.00135],"force_p95":0.70026,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74996,"mean_force":0.16795,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52868,0.00084,0.02529]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":513.0,"contact_point_centroid":[0.57518,0.03772,0.16256],"force_p95":0.42046,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.62658,"mean_force":0.17537,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.56956,0.01923,0.16541]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":552.0,"contact_point_centroid":[0.57239,-0.00042,0.16742],"force_p95":0.38375,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.59548,"mean_force":0.19063,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.56649,0.01808,0.1674]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6737.0,"contact_point_centroid":[0.52948,-0.01803,0.09208],"force_p95":0.11496,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33948,"mean_force":0.07683,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52599,0.0008,0.09001]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7075.0,"contact_point_centroid":[0.52952,0.01956,0.08961],"force_p95":0.1133,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32254,"mean_force":0.07386,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52602,0.0008,0.08776]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00099,-0.00203],"force_p95":0.13171,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15984,"mean_force":0.1253,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.53123,0.00089,0.0255]},{"body_a":"world","body_b":"grasp_target","contact_count":1544.0,"contact_point_centroid":[0.54431,0.00113,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12294,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51686,0.00047,0.24507]},{"body_a":"world","body_b":"grasp_target","contact_count":2084.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53596,0.00098,0.1118]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53095,-0.01833,0.02677],"force_p95":0.07604,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1104,"mean_force":0.05171,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.52997,0.00087,0.02407]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53089,0.01995,0.02588],"force_p95":0.06804,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0965,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.52997,0.00087,0.02407]}],"total_contact_groups":13},"final_pose_error":0.41794,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.67806,0.04039,0.0212],"final_tcp_position":[0.6041,0.04119,0.01118],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":34.7874,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":387.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1544.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53623,0.00096,0.19127],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16544,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":521.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":25.57478,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2084.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53868,0.00103,0.03414],"tcp_start":[0.53623,0.00096,0.19127],"tcp_to_object_dist_end":0.00988,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54415,0.00073,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12962,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15984,"tcp_end":[0.52994,0.00087,0.02403],"tcp_start":[0.53868,0.00103,0.03414],"tcp_to_object_dist_end":0.01433,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":494.0,"n_steps_budget":1000.0,"object_pos_end":[0.54764,0.00087,0.16414],"object_pos_start":[0.54415,0.00073,0.02588],"object_to_goal_dist_end":0.18826,"object_to_goal_dist_start":0.25053,"object_z_max":0.1639,"peak_contact_force":0.11296,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13888.0,"raw_peak_contact_force":0.74996,"tcp_end":[0.52625,0.00081,0.17255],"tcp_start":[0.52994,0.00087,0.02403],"tcp_to_object_dist_end":0.02298,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":76.0,"n_steps_budget":1000.0,"object_pos_end":[0.67806,0.04039,0.0212],"object_pos_start":[0.54764,0.00087,0.16414],"object_to_goal_dist_end":0.20891,"object_to_goal_dist_start":0.18826,"object_z_max":0.16476,"peak_contact_force":13.35108,"phase_name":"approach_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1090.0,"raw_peak_contact_force":34.7874,"subtask_id":"place_at_goal","tcp_end":[0.6041,0.04119,0.01118],"tcp_start":[0.52625,0.00081,0.17255],"tcp_to_object_dist_end":0.07464,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e1209649252ffcf03853fe0727696e22a1eda11729c6c1ae21659980557d7e98`; realized-scene SHA-256: `e32d7866764afb23ec7c7faebb4bcca0aa39fbf2f1ab61f3c9c527b297153af9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.60153,0.17858,0.10809]},{"name":"goal","value":[0.5305,0.03079,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.1828,"average_solve_count":186.0,"average_success_count":186.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.15532,"approach_place.approach_place_height":0.17086,"descend_grasp.descend_speed":0.02051,"lift_object.lift_height":0.1624,"lower_to_place.place_z_offset":-0.00363},"optimized_scores":{"best_composite_score":0.31793,"best_fitness_score":0.74793,"best_task_score":0.53993},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"left_finger","contact_count":1.0,"contact_point_centroid":[0.6022,0.08422,-0.00041],"force_p95":47.64183,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":47.64183,"mean_force":47.64183,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.58849,0.08978,0.01458]},{"body_a":"world","body_b":"grasp_target","contact_count":1.0,"contact_point_centroid":[0.64533,0.16627,-0.00158],"force_p95":2.46211,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.46211,"mean_force":2.46211,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.58849,0.08978,0.01458]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.52721,0.02888,-0.00143],"force_p95":0.69441,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73667,"mean_force":0.16107,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51525,0.0295,0.02604]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":461.0,"contact_point_centroid":[0.55083,0.03571,0.16329],"force_p95":0.38027,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.57476,"mean_force":0.21485,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.5417,0.05326,0.1646]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":398.0,"contact_point_centroid":[0.54517,0.07265,0.16472],"force_p95":0.38197,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.46049,"mean_force":0.12277,"phase_index":4.0,"phase_name":"approach_place","phase_type":"approach","tcp_position_centroid":[0.54251,0.05401,0.1644]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6569.0,"contact_point_centroid":[0.51595,0.01049,0.09052],"force_p95":0.11179,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33293,"mean_force":0.07477,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51268,0.02933,0.08835]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6935.0,"contact_point_centroid":[0.5159,0.04815,0.08742],"force_p95":0.11166,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32985,"mean_force":0.07184,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51271,0.02933,0.08557]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53054,0.03048,-0.00211],"force_p95":0.15557,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23942,"mean_force":0.13152,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.51782,0.02968,0.02604]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4062.0,"contact_point_centroid":[0.51744,0.0104,0.02744],"force_p95":0.07997,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1398,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.51659,0.0296,0.02468]},{"body_a":"world","body_b":"grasp_target","contact_count":1496.0,"contact_point_centroid":[0.5305,0.03079,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51071,0.01327,0.2456]},{"body_a":"world","body_b":"grasp_target","contact_count":2180.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52294,0.02861,0.11232]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4976.0,"contact_point_centroid":[0.51737,0.04875,0.02648],"force_p95":0.07238,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09039,"mean_force":0.04483,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.5166,0.0296,0.02469]}],"total_contact_groups":12},"final_pose_error":0.28417,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.65411,0.18012,0.03206],"final_tcp_position":[0.58701,0.08849,0.00983],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":47.64183,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":375.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1496.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52378,0.02725,0.19182],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16598,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":545.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2180.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52509,0.03017,0.03425],"tcp_start":[0.52378,0.02725,0.19182],"tcp_to_object_dist_end":0.00987,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53037,0.02954,0.02563],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.1846,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14806,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10838.0,"raw_peak_contact_force":0.23942,"tcp_end":[0.51656,0.0296,0.02465],"tcp_start":[0.52509,0.03017,0.03425],"tcp_to_object_dist_end":0.01384,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":470.0,"n_steps_budget":1000.0,"object_pos_end":[0.53377,0.02956,0.15955],"object_pos_start":[0.53037,0.02954,0.02563],"object_to_goal_dist_end":0.1716,"object_to_goal_dist_start":0.1846,"object_z_max":0.1593,"peak_contact_force":0.11843,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13582.0,"raw_peak_contact_force":0.73667,"tcp_end":[0.51289,0.02935,0.16757],"tcp_start":[0.51656,0.0296,0.02465],"tcp_to_object_dist_end":0.02237,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":74.0,"n_steps_budget":1000.0,"object_pos_end":[0.65411,0.18012,0.03206],"object_pos_start":[0.53377,0.02956,0.15955],"object_to_goal_dist_end":0.09245,"object_to_goal_dist_start":0.1716,"object_z_max":0.16012,"peak_contact_force":3.64005,"phase_name":"approach_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":861.0,"raw_peak_contact_force":47.64183,"subtask_id":"place_at_goal","tcp_end":[0.58701,0.08849,0.00983],"tcp_start":[0.51289,0.02935,0.16757],"tcp_to_object_dist_end":0.11573,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```