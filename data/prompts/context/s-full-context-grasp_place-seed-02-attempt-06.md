## Search State

- **Seed**: 2
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → retract → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 12 | -0.1916 | 0.16 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 12 | -0.0927 | 0.35 | ❌ rejected |
| 4 | approach → descend → grasp → lift → retract → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 14 | -0.3226 | 0.16 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.0684 | 0.52 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.0184 | 0.42 | ✅ accepted |

**Proposal policy**: task_score is 0.16 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.192) — your mutation base

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
  - 0.1
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
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_goal_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
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
    arc_height:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: generator.arc_height
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
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_goal_height: status=consumed; consumers=target.offset.z (replace)
    - approach_goal_speed: status=consumed; consumers=generator.speed (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: -0.192
- **task_score** (E): 0.157
- **fitness_score**: 0.558  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.750

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_object | 1.00 | 1.00 | 0.0636 |
| descend_to_grasp | 1.00 | 1.00 | 0.2109 |
| grasp | 1.00 | 1.00 | 0.0116 |
| lift | 1.00 | 0.67 | 0.1289 |
| retract_to_safe_height | 0.67 | 1.00 | 0.2006 |
| approach_above_goal | 1.00 | 1.00 | 0.0054 |
| descend_to_place | 1.00 | 1.00 | 0.0974 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, -0.011, 0.245) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.493, -0.011, 0.245)→(0.489, -0.015, 0.035) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.489, -0.015, 0.035)→(0.480, -0.015, 0.026) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 44.667 | 0.136 | 0.192 |
| lift | lift | 1.00 / step_budget | (0.480, -0.015, 0.026)→(0.477, -0.015, 0.155) | (0.493, -0.015, 0.026)→(0.495, -0.014, 0.136) | 0.281→0.240 | 0.67 / 13.000 | 55983.948 | 0.743 |
| retract_to_safe_height | retract | 0.67 / step_budget | (0.475, -0.015, 0.327)→(0.475, -0.015, 0.528) | (0.495, -0.014, 0.136)→(0.488, -0.001, 0.016) | 0.240→0.279 | 1.00 / 8.333 | 0.123 | 1.712 |
| approach_above_goal | approach | 1.00 / step_budget | (0.624, 0.162, 0.274)→(0.625, 0.164, 0.270) | (0.488, -0.001, 0.016)→(0.488, -0.001, 0.016) | 0.279→0.279 | 1.00 / 8.333 | 90996.391 | 0.123 |
| descend_to_place | descend | 1.00 / step_budget | (0.625, 0.164, 0.270)→(0.631, 0.172, 0.173) | (0.488, -0.001, 0.016)→(0.488, -0.001, 0.016) | 0.279→0.279 | 1.00 / 8.333 | 94251.612 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.180
- phase_score: 0.488
- phase_breakdown.approach_object_score: 0.233
- phase_breakdown.grasp_object_score: 0.729
- phase_breakdown.lift_object_score: 0.000
- phase_breakdown.approach_goal_score: 0.656
- phase_breakdown.place_object_score: 0.823
- grasp_place_fitness: 0.567

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.567
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.180
- **Median Q (composite search score)**: -0.193
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.270


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.60702,"average_solve_count":285.0,"average_success_count":285.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.09204,"approach_above_goal.approach_goal_speed":0.06516,"approach_above_object.approach_height":0.18656,"approach_above_object.approach_speed":0.28598,"descend_to_grasp.descent_speed":0.09586,"descend_to_grasp.grasp_z_tolerance":0.01267,"descend_to_place.place_speed":0.04819,"descend_to_place.place_z_tolerance":0.01529,"lift.lift_height":0.15455,"lift.lift_speed":0.1646,"retract_to_safe_height.retract_height":0.12979,"retract_to_safe_height.retract_speed":0.08115},"optimized_scores":{"best_composite_score":-0.19338,"best_fitness_score":0.55662,"best_task_score":0.15117},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":6796.0,"contact_point_centroid":[0.48722,-0.0118,-0.00214],"force_p95":0.12281,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.68413,"mean_force":0.12879,"phase_index":4.0,"phase_name":"retract_to_safe_height","phase_type":"retract","tcp_position_centroid":[0.45698,-0.01929,0.29079]},{"body_a":"world","body_b":"grasp_target","contact_count":108.0,"contact_point_centroid":[0.47311,-0.01901,-0.00113],"force_p95":0.53905,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.77096,"mean_force":0.07798,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46302,-0.01949,0.02899]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7827.0,"contact_point_centroid":[0.46307,-0.00045,0.08455],"force_p95":0.12017,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35282,"mean_force":0.07016,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46069,-0.01942,0.08246]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8416.0,"contact_point_centroid":[0.46299,-0.03832,0.08239],"force_p95":0.11585,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33249,"mean_force":0.06601,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46068,-0.01942,0.08084]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02,-0.00205],"force_p95":0.13914,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19094,"mean_force":0.12716,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46542,-0.01954,0.02827]},{"body_a":"world","body_b":"grasp_target","contact_count":528.0,"contact_point_centroid":[0.47616,-0.02015,-0.00176],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12355,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.4907,-0.00675,0.26907]},{"body_a":"world","body_b":"grasp_target","contact_count":2504.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47518,-0.01708,0.13355]},{"body_a":"world","body_b":"grasp_target","contact_count":2568.0,"contact_point_centroid":[0.48719,-0.01181,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.53837,0.06511,0.34367]},{"body_a":"world","body_b":"grasp_target","contact_count":952.0,"contact_point_centroid":[0.48719,-0.01181,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62106,0.15162,0.23854]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4820.0,"contact_point_centroid":[0.46433,-0.0003,0.02954],"force_p95":0.0678,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09575,"mean_force":0.04487,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4643,-0.01952,0.02717]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5167.0,"contact_point_centroid":[0.46418,-0.03874,0.02906],"force_p95":0.06657,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08164,"mean_force":0.04298,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46431,-0.01952,0.02718]},{"body_a":"left_finger","body_b":"right_finger","contact_count":6851.0,"contact_point_centroid":[0.45729,-0.0193,0.29771],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01618,"mean_force":0.01064,"phase_index":4.0,"phase_name":"retract_to_safe_height","phase_type":"retract","tcp_position_centroid":[0.45695,-0.01929,0.29543]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2721.0,"contact_point_centroid":[0.53866,0.0651,0.34595],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01279,"mean_force":0.01051,"phase_index":5.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.53836,0.0651,0.34368]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1021.0,"contact_point_centroid":[0.62157,0.15164,0.24075],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01275,"mean_force":0.0104,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62107,0.15163,0.23841]}],"total_contact_groups":14},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.48719,-0.01181,0.01602],"final_tcp_position":[0.62569,0.15615,0.19754],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273005.93995,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":133.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":528.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48067,-0.01455,0.23486],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20897,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":626.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2504.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.47213,-0.01968,0.03494],"tcp_start":[0.48067,-0.01455,0.23486],"tcp_to_object_dist_end":0.0098,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01954,0.0258],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.2882,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.1367,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11787.0,"raw_peak_contact_force":0.19094,"subtask_id":"grasp_object","tcp_end":[0.46428,-0.01951,0.02715],"tcp_start":[0.47213,-0.01968,0.03494],"tcp_to_object_dist_end":0.01183,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.48375,-0.01877,0.14285],"object_pos_start":[0.47603,-0.01954,0.0258],"object_to_goal_dist_end":0.23601,"object_to_goal_dist_start":0.2882,"object_z_max":0.14716,"peak_contact_force":0.0,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16351.0,"raw_peak_contact_force":0.77096,"subtask_id":"lift_object","tcp_end":[0.46087,-0.01941,0.16671],"tcp_start":[0.46428,-0.01951,0.02715],"tcp_to_object_dist_end":0.03306,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1766.0,"n_steps_budget":990.0,"object_pos_end":[0.48719,-0.01181,0.01602],"object_pos_start":[0.48375,-0.01877,0.14285],"object_to_goal_dist_end":0.2834,"object_to_goal_dist_start":0.23601,"object_z_max":0.14285,"peak_contact_force":0.12263,"phase_name":"retract_to_safe_height","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":13647.0,"raw_peak_contact_force":1.68413,"subtask_id":"lift_object","tcp_end":[0.45685,-0.01931,0.41084],"tcp_start":[0.45818,-0.01933,0.28598],"tcp_to_object_dist_end":0.39606,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":642.0,"n_steps_budget":1000.0,"object_pos_end":[0.48719,-0.01181,0.01602],"object_pos_start":[0.48719,-0.01181,0.01602],"object_to_goal_dist_end":0.2834,"object_to_goal_dist_start":0.2834,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5289.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_goal","tcp_end":[0.61835,0.14792,0.2796],"tcp_start":[0.61705,0.14583,0.28306],"tcp_to_object_dist_end":0.33495,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":238.0,"n_steps_budget":1000.0,"object_pos_end":[0.48719,-0.01181,0.01602],"object_pos_start":[0.48719,-0.01181,0.01602],"object_to_goal_dist_end":0.2834,"object_to_goal_dist_start":0.2834,"object_z_max":0.01602,"peak_contact_force":273005.93995,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1973.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.62569,0.15615,0.19754],"tcp_start":[0.61835,0.14792,0.2796],"tcp_to_object_dist_end":0.28344,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62644,"average_solve_count":348.0,"average_success_count":348.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.10368,"approach_above_goal.approach_goal_speed":0.06001,"approach_above_object.approach_height":0.2046,"approach_above_object.approach_speed":0.14019,"descend_to_grasp.descent_speed":0.05831,"descend_to_grasp.grasp_z_tolerance":0.01314,"descend_to_place.place_speed":0.05443,"descend_to_place.place_z_tolerance":0.00933,"lift.lift_height":0.10562,"lift.lift_speed":0.17334,"retract_to_safe_height.retract_height":0.24658,"retract_to_safe_height.retract_speed":0.18759},"optimized_scores":{"best_composite_score":-0.19832,"best_fitness_score":0.55168,"best_task_score":0.13974},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":5133.0,"contact_point_centroid":[0.4562,-0.00917,-0.00218],"force_p95":0.12359,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.73435,"mean_force":0.13252,"phase_index":4.0,"phase_name":"retract_to_safe_height","phase_type":"retract","tcp_position_centroid":[0.44126,-0.02518,0.39192]},{"body_a":"world","body_b":"grasp_target","contact_count":126.0,"contact_point_centroid":[0.45515,-0.02491,-0.00127],"force_p95":0.51289,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6929,"mean_force":0.10597,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44602,-0.02539,0.02941]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2082.0,"contact_point_centroid":[0.44671,-0.04364,0.1438],"force_p95":0.17065,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34656,"mean_force":0.09746,"phase_index":4.0,"phase_name":"retract_to_safe_height","phase_type":"retract","tcp_position_centroid":[0.44095,-0.02515,0.14349]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9300.0,"contact_point_centroid":[0.44508,-0.04428,0.06963],"force_p95":0.1017,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28253,"mean_force":0.05883,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44364,-0.02529,0.06786]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8770.0,"contact_point_centroid":[0.44528,-0.00627,0.07061],"force_p95":0.10059,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28212,"mean_force":0.06147,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44366,-0.02529,0.06852]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2048.0,"contact_point_centroid":[0.44672,-0.00666,0.14491],"force_p95":0.16909,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28114,"mean_force":0.09869,"phase_index":4.0,"phase_name":"retract_to_safe_height","phase_type":"retract","tcp_position_centroid":[0.44089,-0.02515,0.1447]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02615,-0.00208],"force_p95":0.14567,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22348,"mean_force":0.12898,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44844,-0.02547,0.02893]},{"body_a":"world","body_b":"grasp_target","contact_count":480.0,"contact_point_centroid":[0.45856,-0.02632,-0.00174],"force_p95":0.13798,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12365,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.48517,-0.00856,0.27607]},{"body_a":"world","body_b":"grasp_target","contact_count":2928.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46055,-0.02207,0.14078]},{"body_a":"world","body_b":"grasp_target","contact_count":3756.0,"contact_point_centroid":[0.45616,-0.00916,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.5316,0.08594,0.40496]},{"body_a":"world","body_b":"grasp_target","contact_count":1152.0,"contact_point_centroid":[0.45616,-0.00916,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62028,0.2007,0.17117]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5284.0,"contact_point_centroid":[0.44674,-0.00619,0.02939],"force_p95":0.06577,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10457,"mean_force":0.04113,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44735,-0.02543,0.02791]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5439.0,"contact_point_centroid":[0.44674,-0.04473,0.02925],"force_p95":0.06576,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08178,"mean_force":0.04118,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44736,-0.02543,0.02791]},{"body_a":"left_finger","body_b":"right_finger","contact_count":5177.0,"contact_point_centroid":[0.44166,-0.02519,0.40398],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01058,"phase_index":4.0,"phase_name":"retract_to_safe_height","phase_type":"retract","tcp_position_centroid":[0.4413,-0.02519,0.40163]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4015.0,"contact_point_centroid":[0.53215,0.08616,0.40687],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01289,"mean_force":0.01043,"phase_index":5.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.53178,0.08616,0.4046]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1225.0,"contact_point_centroid":[0.62081,0.20071,0.17351],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01279,"mean_force":0.01048,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62028,0.20069,0.17122]}],"total_contact_groups":16},"final_pose_error":0.00977,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.45616,-0.00916,0.01602],"final_tcp_position":[0.62418,0.20508,0.1212],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9748.77463,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":121.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12254,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":480.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.46878,-0.01854,0.24955],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22389,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":732.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2928.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.45492,-0.02569,0.03512],"tcp_start":[0.46878,-0.01854,0.24955],"tcp_to_object_dist_end":0.00982,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45845,-0.02552,0.02572],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30319,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14266,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12523.0,"raw_peak_contact_force":0.22348,"subtask_id":"grasp_object","tcp_end":[0.44733,-0.02543,0.02788],"tcp_start":[0.45492,-0.02569,0.03512],"tcp_to_object_dist_end":0.01133,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":526.0,"n_steps_budget":600.0,"object_pos_end":[0.46094,-0.02533,0.1108],"object_pos_start":[0.45845,-0.02552,0.02572],"object_to_goal_dist_end":0.28841,"object_to_goal_dist_start":0.30319,"object_z_max":0.11069,"peak_contact_force":0.11422,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18196.0,"raw_peak_contact_force":0.6929,"subtask_id":"lift_object","tcp_end":[0.44355,-0.02527,0.12175],"tcp_start":[0.44733,-0.02543,0.02788],"tcp_to_object_dist_end":0.02055,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1566.0,"n_steps_budget":840.0,"object_pos_end":[0.45616,-0.00916,0.01602],"object_pos_start":[0.46094,-0.02533,0.1108],"object_to_goal_dist_end":0.2952,"object_to_goal_dist_start":0.28841,"object_z_max":0.15413,"peak_contact_force":0.12263,"phase_name":"retract_to_safe_height","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":14440.0,"raw_peak_contact_force":1.73435,"subtask_id":"lift_object","tcp_end":[0.44267,-0.02528,0.58831],"tcp_start":[0.4418,-0.0252,0.35188],"tcp_to_object_dist_end":0.57268,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":939.0,"n_steps_budget":1000.0,"object_pos_end":[0.45616,-0.00916,0.01602],"object_pos_start":[0.45616,-0.00916,0.01602],"object_to_goal_dist_end":0.2952,"object_to_goal_dist_start":0.2952,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7771.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_goal","tcp_end":[0.61879,0.19737,0.22222],"tcp_start":[0.61829,0.19557,0.22766],"tcp_to_object_dist_end":0.3341,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":288.0,"n_steps_budget":1000.0,"object_pos_end":[0.45616,-0.00916,0.01602],"object_pos_start":[0.45616,-0.00916,0.01602],"object_to_goal_dist_end":0.2952,"object_to_goal_dist_start":0.2952,"object_z_max":0.01602,"peak_contact_force":9748.77463,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2377.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.62418,0.20508,0.1212],"tcp_start":[0.61879,0.19737,0.22222],"tcp_to_object_dist_end":0.29188,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.66667,"average_solve_count":324.0,"average_success_count":324.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.10966,"approach_above_goal.approach_goal_speed":0.08294,"approach_above_object.approach_height":0.20861,"approach_above_object.approach_speed":0.18751,"descend_to_grasp.descent_speed":0.06988,"descend_to_grasp.grasp_z_tolerance":0.01606,"descend_to_place.place_speed":0.04988,"descend_to_place.place_z_tolerance":0.01057,"lift.lift_height":0.16757,"lift.lift_speed":0.12529,"retract_to_safe_height.retract_height":0.24978,"retract_to_safe_height.retract_speed":0.10378},"optimized_scores":{"best_composite_score":-0.18307,"best_fitness_score":0.56693,"best_task_score":0.18014},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":7342.0,"contact_point_centroid":[0.5211,0.01872,-0.00211],"force_p95":0.12292,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.71864,"mean_force":0.12976,"phase_index":4.0,"phase_name":"retract_to_safe_height","phase_type":"retract","tcp_position_centroid":[0.52347,0.00071,0.36548]},{"body_a":"world","body_b":"grasp_target","contact_count":166.0,"contact_point_centroid":[0.54097,0.00071,-0.00116],"force_p95":0.52534,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.76476,"mean_force":0.11653,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52797,0.00082,0.02534]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9750.0,"contact_point_centroid":[0.52914,-0.01794,0.087],"force_p95":0.14499,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33986,"mean_force":0.08223,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52556,0.00079,0.08586]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10374.0,"contact_point_centroid":[0.52917,0.01945,0.08544],"force_p95":0.14128,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32911,"mean_force":0.07867,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52559,0.00079,0.08458]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":207.0,"contact_point_centroid":[0.52934,0.01685,0.17283],"force_p95":0.24601,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26933,"mean_force":0.14752,"phase_index":4.0,"phase_name":"retract_to_safe_height","phase_type":"retract","tcp_position_centroid":[0.52524,0.00078,0.17855]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":64.0,"contact_point_centroid":[0.53089,-0.01689,0.17131],"force_p95":0.15745,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16526,"mean_force":0.10162,"phase_index":4.0,"phase_name":"retract_to_safe_height","phase_type":"retract","tcp_position_centroid":[0.52583,0.0008,0.17739]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00098,-0.00203],"force_p95":0.13176,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16054,"mean_force":0.1253,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53101,0.00088,0.02528]},{"body_a":"world","body_b":"grasp_target","contact_count":492.0,"contact_point_centroid":[0.54431,0.00113,-0.00174],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12362,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.51358,0.00037,0.27654]},{"body_a":"world","body_b":"grasp_target","contact_count":2744.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.5325,0.00088,0.14065]},{"body_a":"world","body_b":"grasp_target","contact_count":2552.0,"contact_point_centroid":[0.52104,0.01871,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.58255,0.07376,0.44507]},{"body_a":"world","body_b":"grasp_target","contact_count":1160.0,"contact_point_centroid":[0.52104,0.01871,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63967,0.15133,0.25291]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53081,-0.01834,0.02654],"force_p95":0.07605,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11019,"mean_force":0.0517,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52976,0.00086,0.02385]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53074,0.01994,0.02566],"force_p95":0.06805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09675,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52976,0.00086,0.02386]},{"body_a":"left_finger","body_b":"right_finger","contact_count":7659.0,"contact_point_centroid":[0.5238,0.00072,0.37281],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01643,"mean_force":0.01044,"phase_index":4.0,"phase_name":"retract_to_safe_height","phase_type":"retract","tcp_position_centroid":[0.5235,0.00071,0.3705]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2734.0,"contact_point_centroid":[0.58288,0.07351,0.44786],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01041,"phase_index":5.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.58236,0.0735,0.44555]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1245.0,"contact_point_centroid":[0.64023,0.15135,0.25524],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01269,"mean_force":0.0104,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63967,0.15133,0.25293]}],"total_contact_groups":16},"final_pose_error":0.00974,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.52104,0.01871,0.01602],"final_tcp_position":[0.64289,0.15558,0.19924],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":272988.92809,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":124.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12257,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":492.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52913,0.00077,0.25118],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22567,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":686.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2744.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.53847,0.00102,0.03392],"tcp_start":[0.52913,0.00077,0.25118],"tcp_to_object_dist_end":0.00982,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54415,0.00072,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12964,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.16054,"subtask_id":"grasp_object","tcp_end":[0.52973,0.00086,0.02382],"tcp_start":[0.53847,0.00102,0.03392],"tcp_to_object_dist_end":0.01457,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":782.0,"n_steps_budget":840.0,"object_pos_end":[0.53907,0.00073,0.15474],"object_pos_start":[0.54415,0.00072,0.02588],"object_to_goal_dist_end":0.19459,"object_to_goal_dist_start":0.25053,"object_z_max":0.15467,"peak_contact_force":167951.73011,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20290.0,"raw_peak_contact_force":0.76476,"subtask_id":"lift_object","tcp_end":[0.52604,0.0008,0.177],"tcp_start":[0.52973,0.00086,0.02382],"tcp_to_object_dist_end":0.02579,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1938.0,"n_steps_budget":1000.0,"object_pos_end":[0.52104,0.01871,0.01602],"object_pos_start":[0.53907,0.00073,0.15474],"object_to_goal_dist_end":0.2571,"object_to_goal_dist_start":0.19459,"object_z_max":0.15474,"peak_contact_force":0.12263,"phase_name":"retract_to_safe_height","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":15272.0,"raw_peak_contact_force":1.71864,"subtask_id":"lift_object","tcp_end":[0.5255,0.00066,0.58405],"tcp_start":[0.52396,0.00075,0.34356],"tcp_to_object_dist_end":0.56834,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":638.0,"n_steps_budget":1000.0,"object_pos_end":[0.52104,0.01871,0.01602],"object_pos_start":[0.52104,0.01871,0.01602],"object_to_goal_dist_end":0.2571,"object_to_goal_dist_start":0.2571,"object_z_max":0.01602,"peak_contact_force":272988.92809,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5286.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_goal","tcp_end":[0.63813,0.14786,0.30688],"tcp_start":[0.63726,0.14593,0.31264],"tcp_to_object_dist_end":0.33909,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":290.0,"n_steps_budget":1000.0,"object_pos_end":[0.52104,0.01871,0.01602],"object_pos_start":[0.52104,0.01871,0.01602],"object_to_goal_dist_end":0.2571,"object_to_goal_dist_start":0.2571,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2405.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.64289,0.15558,0.19924],"tcp_start":[0.63813,0.14786,0.30688],"tcp_to_object_dist_end":0.25913,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```