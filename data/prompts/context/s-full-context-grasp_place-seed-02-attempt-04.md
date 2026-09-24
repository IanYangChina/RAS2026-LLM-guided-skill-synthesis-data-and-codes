## Search State

- **Seed**: 2
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → retract → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 14 | -0.3226 | 0.16 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.0684 | 0.52 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.0184 | 0.42 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | 0.0200 | 0.38 | ✅ accepted |
| 0 | align → align → pull → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | contact_detected | 0 | 0.1073 | 0.16 | ✅ accepted |

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

## Current Skill (Q=-0.323) — your mutation base

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

- **Composite score**: -0.323
- **task_score** (E): 0.155
- **fitness_score**: 0.557  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.880

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_object | 1.00 | 1.00 | 0.0903 |
| descend_to_grasp | 1.00 | 1.00 | 0.1830 |
| grasp | 1.00 | 1.00 | 0.0116 |
| lift | 1.00 | 0.67 | 0.1405 |
| retract_to_clearance | 1.00 | 1.00 | 0.1961 |
| approach_above_goal | 1.00 | 1.00 | 0.2351 |
| descend_to_place | 1.00 | 1.00 | 0.1252 |
| release_object | 1.00 | 1.00 | 0.0188 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.490, -0.012, 0.218) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 14.548 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.490, -0.012, 0.218)→(0.488, -0.015, 0.035) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.488, -0.015, 0.035)→(0.480, -0.015, 0.026) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 45.000 | 0.136 | 0.187 |
| lift | lift | 1.00 / step_budget | (0.480, -0.015, 0.026)→(0.477, -0.015, 0.167) | (0.493, -0.015, 0.026)→(0.496, -0.014, 0.141) | 0.281→0.240 | 0.67 / 12.667 | 0.038 | 0.760 |
| retract_to_clearance | retract | 1.00 / step_budget | (0.477, -0.015, 0.167)→(0.475, -0.015, 0.363) | (0.496, -0.014, 0.141)→(0.486, -0.002, 0.016) | 0.240→0.281 | 1.00 / 8.667 | 94251.011 | 1.788 |
| approach_above_goal | approach | 1.00 / step_budget | (0.475, -0.015, 0.363)→(0.624, 0.161, 0.322) | (0.486, -0.002, 0.016)→(0.486, -0.002, 0.016) | 0.281→0.281 | 1.00 / 8.000 | 6499.283 | 0.123 |
| descend_to_place | descend | 1.00 / step_budget | (0.624, 0.161, 0.322)→(0.631, 0.171, 0.198) | (0.486, -0.002, 0.016)→(0.486, -0.002, 0.016) | 0.281→0.281 | 1.00 / 8.667 | 185253.811 | 0.123 |
| release_object | release | 1.00 / step_budget | (0.631, 0.171, 0.198)→(0.626, 0.170, 0.215) | (0.486, -0.002, 0.016)→(0.486, -0.002, 0.016) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.185
- phase_score: 0.420
- phase_breakdown.approach_object_score: 0.184
- phase_breakdown.grasp_object_score: 0.729
- phase_breakdown.lift_object_score: 0.208
- phase_breakdown.approach_goal_score: 0.645
- phase_breakdown.place_object_score: 0.334
- grasp_place_fitness: 0.569

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.569
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.185
- **Median Q (composite search score)**: -0.326
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.232


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.13158,"average_solve_count":190.0,"average_success_count":190.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.15857,"approach_above_goal.approach_goal_speed":0.16346,"approach_above_object.approach_height":0.13353,"approach_above_object.approach_speed":0.1529,"descend_to_grasp.descent_speed":0.1128,"descend_to_grasp.grasp_z_tolerance":0.01368,"descend_to_place.place_speed":0.06929,"descend_to_place.place_z_offset":0.0153,"descend_to_place.place_z_tolerance":0.01355,"lift.lift_height":0.19018,"lift.lift_speed":0.15591,"release_object.release_duration":1.46691,"retract_to_clearance.retract_height":0.20444,"retract_to_clearance.retract_speed":0.1028},"optimized_scores":{"best_composite_score":-0.33107,"best_fitness_score":0.54893,"best_task_score":0.13641},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1904.0,"contact_point_centroid":[0.47133,-0.02345,-0.00259],"force_p95":0.2298,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.7874,"mean_force":0.14693,"phase_index":4.0,"phase_name":"retract_to_clearance","phase_type":"retract","tcp_position_centroid":[0.45871,-0.01939,0.30947]},{"body_a":"world","body_b":"grasp_target","contact_count":120.0,"contact_point_centroid":[0.47336,-0.01911,-0.0011],"force_p95":0.52315,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.76123,"mean_force":0.07343,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46275,-0.01953,0.02908]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10113.0,"contact_point_centroid":[0.46335,-0.00059,0.10013],"force_p95":0.127,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34708,"mean_force":0.07337,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46049,-0.01945,0.09848]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10582.0,"contact_point_centroid":[0.46333,-0.03829,0.09815],"force_p95":0.12415,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33051,"mean_force":0.07077,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46049,-0.01946,0.09685]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":36.0,"contact_point_centroid":[0.46689,-0.03801,0.19733],"force_p95":0.2061,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22851,"mean_force":0.07071,"phase_index":4.0,"phase_name":"retract_to_clearance","phase_type":"retract","tcp_position_centroid":[0.46053,-0.01944,0.20353]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":40.0,"contact_point_centroid":[0.46766,-0.00177,0.19727],"force_p95":0.18887,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18949,"mean_force":0.05554,"phase_index":4.0,"phase_name":"retract_to_clearance","phase_type":"retract","tcp_position_centroid":[0.46055,-0.01944,0.20347]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02002,-0.00205],"force_p95":0.13838,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18934,"mean_force":0.12697,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46522,-0.01958,0.02828]},{"body_a":"world","body_b":"grasp_target","contact_count":860.0,"contact_point_centroid":[0.47616,-0.02015,-0.00185],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1232,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.48889,-0.00784,0.24299]},{"body_a":"world","body_b":"grasp_target","contact_count":1844.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47348,-0.01805,0.10776]},{"body_a":"world","body_b":"grasp_target","contact_count":2116.0,"contact_point_centroid":[0.47122,-0.02343,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.53807,0.06273,0.3642]},{"body_a":"world","body_b":"grasp_target","contact_count":852.0,"contact_point_centroid":[0.47122,-0.02343,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62157,0.15043,0.28528]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.47122,-0.02343,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62238,0.15461,0.22255]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5062.0,"contact_point_centroid":[0.46379,-0.00034,0.02976],"force_p95":0.06596,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09492,"mean_force":0.04287,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4641,-0.01956,0.02718]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5162.0,"contact_point_centroid":[0.46402,-0.03881,0.02916],"force_p95":0.06671,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08299,"mean_force":0.04304,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4641,-0.01956,0.02718]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1767.0,"contact_point_centroid":[0.45904,-0.01939,0.32142],"force_p95":0.01183,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01646,"mean_force":0.01072,"phase_index":4.0,"phase_name":"retract_to_clearance","phase_type":"retract","tcp_position_centroid":[0.45877,-0.01939,0.31911]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2257.0,"contact_point_centroid":[0.53887,0.0632,0.36627],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.01045,"phase_index":5.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.53853,0.0632,0.36407]}],"total_contact_groups":18},"final_pose_error":0.01946,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.47122,-0.02343,0.01602],"final_tcp_position":[0.62623,0.1557,0.22374],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273006.54034,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":216.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":860.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.47766,-0.01646,0.18284],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15687,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":461.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1844.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.47192,-0.01972,0.03494],"tcp_start":[0.47766,-0.01646,0.18284],"tcp_to_object_dist_end":0.00989,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.0196,0.02581],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28824,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13612,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12024.0,"raw_peak_contact_force":0.18934,"subtask_id":"grasp_object","tcp_end":[0.46407,-0.01955,0.02715],"tcp_start":[0.47192,-0.01972,0.03494],"tcp_to_object_dist_end":0.01203,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":722.0,"n_steps_budget":780.0,"object_pos_end":[0.47648,-0.01943,0.18142],"object_pos_start":[0.47603,-0.0196,0.02581],"object_to_goal_dist_end":0.23662,"object_to_goal_dist_start":0.28824,"object_z_max":0.18134,"peak_contact_force":0.01017,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20815.0,"raw_peak_contact_force":0.76123,"subtask_id":"lift_object","tcp_end":[0.46088,-0.01945,0.20284],"tcp_start":[0.46407,-0.01955,0.02715],"tcp_to_object_dist_end":0.02649,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":567.0,"n_steps_budget":1000.0,"object_pos_end":[0.47122,-0.02343,0.01602],"object_pos_start":[0.47648,-0.01943,0.18142],"object_to_goal_dist_end":0.29882,"object_to_goal_dist_start":0.23662,"object_z_max":0.18142,"peak_contact_force":9748.79603,"phase_name":"retract_to_clearance","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3747.0,"raw_peak_contact_force":1.7874,"subtask_id":"lift_object","tcp_end":[0.45946,-0.01942,0.38749],"tcp_start":[0.46088,-0.01945,0.20284],"tcp_to_object_dist_end":0.37168,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":529.0,"n_steps_budget":1000.0,"object_pos_end":[0.47122,-0.02343,0.01602],"object_pos_start":[0.47122,-0.02343,0.01602],"object_to_goal_dist_end":0.29882,"object_to_goal_dist_start":0.29882,"object_z_max":0.01602,"peak_contact_force":9748.94121,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4373.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_goal","tcp_end":[0.61782,0.14567,0.34383],"tcp_start":[0.45946,-0.01942,0.38749],"tcp_to_object_dist_end":0.39692,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":213.0,"n_steps_budget":1000.0,"object_pos_end":[0.47122,-0.02343,0.01602],"object_pos_start":[0.47122,-0.02343,0.01602],"object_to_goal_dist_end":0.29882,"object_to_goal_dist_start":0.29882,"object_z_max":0.01602,"peak_contact_force":273006.54034,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1771.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.62623,0.1557,0.22374],"tcp_start":[0.61782,0.14567,0.34383],"tcp_to_object_dist_end":0.31507,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47122,-0.02343,0.01602],"object_pos_start":[0.47122,-0.02343,0.01602],"object_to_goal_dist_end":0.29882,"object_to_goal_dist_start":0.29882,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.62115,0.15418,0.24199],"tcp_start":[0.62623,0.1557,0.22374],"tcp_to_object_dist_end":0.32418,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":212.0,"average_success_count":212.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.15857,"approach_above_goal.approach_goal_speed":0.11727,"approach_above_object.approach_height":0.15874,"approach_above_object.approach_speed":0.13035,"descend_to_grasp.descent_speed":0.08584,"descend_to_grasp.grasp_z_tolerance":0.01201,"descend_to_place.place_speed":0.07397,"descend_to_place.place_z_offset":0.00893,"descend_to_place.place_z_tolerance":0.02245,"lift.lift_height":0.15176,"lift.lift_speed":0.16053,"release_object.release_duration":1.2071,"retract_to_clearance.retract_height":0.19979,"retract_to_clearance.retract_speed":0.12729},"optimized_scores":{"best_composite_score":-0.32594,"best_fitness_score":0.55406,"best_task_score":0.14477},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1921.0,"contact_point_centroid":[0.47382,-0.01528,-0.00247],"force_p95":0.20379,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.62807,"mean_force":0.14439,"phase_index":4.0,"phase_name":"retract_to_clearance","phase_type":"retract","tcp_position_centroid":[0.44151,-0.02522,0.26319]},{"body_a":"world","body_b":"grasp_target","contact_count":109.0,"contact_point_centroid":[0.45576,-0.0246,-0.00114],"force_p95":0.54694,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.7726,"mean_force":0.07647,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44601,-0.02545,0.02983]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7682.0,"contact_point_centroid":[0.44602,-0.00639,0.08175],"force_p95":0.12035,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32594,"mean_force":0.06901,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44376,-0.02535,0.07973]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8134.0,"contact_point_centroid":[0.44593,-0.04428,0.08007],"force_p95":0.11632,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3217,"mean_force":0.06587,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44374,-0.02535,0.07852]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02616,-0.00207],"force_p95":0.14381,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21048,"mean_force":0.12846,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44834,-0.02553,0.02898]},{"body_a":"world","body_b":"grasp_target","contact_count":744.0,"contact_point_centroid":[0.45856,-0.02632,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12328,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.48282,-0.00988,0.25483]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5287.0,"contact_point_centroid":[0.44666,-0.00624,0.02952],"force_p95":0.06555,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12962,"mean_force":0.04113,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44726,-0.02549,0.02796]},{"body_a":"world","body_b":"grasp_target","contact_count":2220.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45852,-0.02324,0.11993]},{"body_a":"world","body_b":"grasp_target","contact_count":2832.0,"contact_point_centroid":[0.4737,-0.01526,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.52891,0.08415,0.30529]},{"body_a":"world","body_b":"grasp_target","contact_count":892.0,"contact_point_centroid":[0.4737,-0.01526,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62002,0.19841,0.20693]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.4737,-0.01526,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61904,0.20234,0.14]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5433.0,"contact_point_centroid":[0.44666,-0.04479,0.02938],"force_p95":0.06562,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08075,"mean_force":0.04118,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44727,-0.02549,0.02796]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1740.0,"contact_point_centroid":[0.44182,-0.02523,0.27693],"force_p95":0.0119,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01625,"mean_force":0.01072,"phase_index":4.0,"phase_name":"retract_to_clearance","phase_type":"retract","tcp_position_centroid":[0.44152,-0.02522,0.27468]},{"body_a":"left_finger","body_b":"right_finger","contact_count":953.0,"contact_point_centroid":[0.62048,0.19844,0.20895],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.01044,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62004,0.19843,0.20656]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3024.0,"contact_point_centroid":[0.52919,0.08414,0.3075],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.01044,"phase_index":5.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.5289,0.08414,0.30529]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.6224,0.20344,0.1386],"force_p95":0.01091,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01092,"mean_force":0.01,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62182,0.20342,0.13629]}],"total_contact_groups":16},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.4737,-0.01526,0.01602],"final_tcp_position":[0.62419,0.2041,0.14168],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9748.8403,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":187.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":43.39807,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":744.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.46468,-0.02084,0.20683],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.181,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":555.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2220.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.45487,-0.02575,0.0352],"tcp_start":[0.46468,-0.02084,0.20683],"tcp_to_object_dist_end":0.00991,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02557,0.02574],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30322,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14109,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12520.0,"raw_peak_contact_force":0.21048,"subtask_id":"grasp_object","tcp_end":[0.44724,-0.02549,0.02793],"tcp_start":[0.45487,-0.02575,0.0352],"tcp_to_object_dist_end":0.01142,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.47042,-0.02344,0.12096],"object_pos_start":[0.45844,-0.02557,0.02574],"object_to_goal_dist_end":0.28146,"object_to_goal_dist_start":0.30322,"object_z_max":0.14097,"peak_contact_force":0.0,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15925.0,"raw_peak_contact_force":0.7726,"subtask_id":"lift_object","tcp_end":[0.44389,-0.02533,0.16519],"tcp_start":[0.44724,-0.02549,0.02793],"tcp_to_object_dist_end":0.05161,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":529.0,"n_steps_budget":990.0,"object_pos_end":[0.4737,-0.01526,0.01602],"object_pos_start":[0.47042,-0.02344,0.12096],"object_to_goal_dist_end":0.28989,"object_to_goal_dist_start":0.28146,"object_z_max":0.12096,"peak_contact_force":0.12263,"phase_name":"retract_to_clearance","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3661.0,"raw_peak_contact_force":1.62807,"subtask_id":"lift_object","tcp_end":[0.44214,-0.02526,0.34518],"tcp_start":[0.44389,-0.02533,0.16519],"tcp_to_object_dist_end":0.33082,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":708.0,"n_steps_budget":1000.0,"object_pos_end":[0.4737,-0.01526,0.01602],"object_pos_start":[0.4737,-0.01526,0.01602],"object_to_goal_dist_end":0.28989,"object_to_goal_dist_start":0.28989,"object_z_max":0.01602,"peak_contact_force":9748.78517,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5856.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_goal","tcp_end":[0.61721,0.19341,0.26935],"tcp_start":[0.44214,-0.02526,0.34518],"tcp_to_object_dist_end":0.35821,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":223.0,"n_steps_budget":1000.0,"object_pos_end":[0.4737,-0.01526,0.01602],"object_pos_start":[0.4737,-0.01526,0.01602],"object_to_goal_dist_end":0.28989,"object_to_goal_dist_start":0.28989,"object_z_max":0.01602,"peak_contact_force":9748.8403,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1845.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.62419,0.2041,0.14168],"tcp_start":[0.61721,0.19341,0.26935],"tcp_to_object_dist_end":0.2942,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4737,-0.01526,0.01602],"object_pos_start":[0.4737,-0.01526,0.01602],"object_to_goal_dist_end":0.28989,"object_to_goal_dist_start":0.28989,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.61732,0.20166,0.15938],"tcp_start":[0.62419,0.2041,0.14168],"tcp_to_object_dist_end":0.29705,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72619,"average_solve_count":252.0,"average_success_count":252.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.17057,"approach_above_goal.approach_goal_speed":0.10565,"approach_above_object.approach_height":0.22234,"approach_above_object.approach_speed":0.21412,"descend_to_grasp.descent_speed":0.06932,"descend_to_grasp.grasp_z_tolerance":0.01444,"descend_to_place.place_speed":0.07531,"descend_to_place.place_z_offset":0.01717,"descend_to_place.place_z_tolerance":0.02519,"lift.lift_height":0.15435,"lift.lift_speed":0.06653,"release_object.release_duration":1.02136,"retract_to_clearance.retract_height":0.24334,"retract_to_clearance.retract_speed":0.11098},"optimized_scores":{"best_composite_score":-0.3108,"best_fitness_score":0.5692,"best_task_score":0.18476},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1105.0,"contact_point_centroid":[0.5151,0.03243,-0.00297],"force_p95":0.5635,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.94816,"mean_force":0.17858,"phase_index":4.0,"phase_name":"retract_to_clearance","phase_type":"retract","tcp_position_centroid":[0.52317,0.00074,0.31329]},{"body_a":"world","body_b":"grasp_target","contact_count":166.0,"contact_point_centroid":[0.54013,0.00046,-0.00111],"force_p95":0.50912,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74694,"mean_force":0.11551,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52796,0.00082,0.02556]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4132.0,"contact_point_centroid":[0.52584,0.01908,0.17855],"force_p95":0.15334,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37794,"mean_force":0.09043,"phase_index":4.0,"phase_name":"retract_to_clearance","phase_type":"retract","tcp_position_centroid":[0.52241,0.00074,0.18063]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16547.0,"contact_point_centroid":[0.52714,-0.01821,0.07671],"force_p95":0.08964,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33342,"mean_force":0.06205,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52518,0.00078,0.07516]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17003.0,"contact_point_centroid":[0.52726,0.01974,0.07601],"force_p95":0.0886,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32143,"mean_force":0.06065,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52521,0.00078,0.0746]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3815.0,"contact_point_centroid":[0.52571,-0.01777,0.17501],"force_p95":0.15955,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26872,"mean_force":0.09099,"phase_index":4.0,"phase_name":"retract_to_clearance","phase_type":"retract","tcp_position_centroid":[0.52241,0.00074,0.17716]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00098,-0.00203],"force_p95":0.13178,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16057,"mean_force":0.1253,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53097,0.00088,0.02542]},{"body_a":"world","body_b":"grasp_target","contact_count":424.0,"contact_point_centroid":[0.54431,0.00113,-0.00171],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1238,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.51292,0.00035,0.28241]},{"body_a":"world","body_b":"grasp_target","contact_count":2892.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53185,0.00086,0.14647]},{"body_a":"world","body_b":"grasp_target","contact_count":1912.0,"contact_point_centroid":[0.51449,0.03244,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.57936,0.07232,0.35225]},{"body_a":"world","body_b":"grasp_target","contact_count":864.0,"contact_point_centroid":[0.51449,0.03244,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63928,0.14907,0.29211]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51449,0.03244,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.63928,0.15354,0.22558]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53078,-0.01834,0.02668],"force_p95":0.07605,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11032,"mean_force":0.0517,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52972,0.00086,0.02399]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53071,0.01994,0.0258],"force_p95":0.06806,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09676,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52972,0.00086,0.02399]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1040.0,"contact_point_centroid":[0.52359,0.00074,0.32016],"force_p95":0.01275,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01629,"mean_force":0.01079,"phase_index":4.0,"phase_name":"retract_to_clearance","phase_type":"retract","tcp_position_centroid":[0.52322,0.00074,0.31796]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2055.0,"contact_point_centroid":[0.57949,0.07195,0.35452],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01273,"mean_force":0.01037,"phase_index":5.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.57907,0.07194,0.35226]}],"total_contact_groups":18},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.51449,0.03244,0.01602],"final_tcp_position":[0.64307,0.15458,0.22741],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273006.05362,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":107.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12236,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":424.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52779,0.00073,0.2629],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23745,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":723.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2892.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.53841,0.00102,0.03403],"tcp_start":[0.52779,0.00073,0.2629],"tcp_to_object_dist_end":0.00995,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54415,0.00072,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12966,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.16057,"subtask_id":"grasp_object","tcp_end":[0.52969,0.00086,0.02395],"tcp_start":[0.53841,0.00102,0.03403],"tcp_to_object_dist_end":0.01459,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53992,0.00076,0.12038],"object_pos_start":[0.54415,0.00072,0.02588],"object_to_goal_dist_end":0.20335,"object_to_goal_dist_start":0.25053,"object_z_max":0.12028,"peak_contact_force":0.10436,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33716.0,"raw_peak_contact_force":0.74694,"subtask_id":"lift_object","tcp_end":[0.52538,0.00079,0.13222],"tcp_start":[0.52969,0.00086,0.02395],"tcp_to_object_dist_end":0.01875,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":733.0,"n_steps_budget":1000.0,"object_pos_end":[0.51449,0.03244,0.01602],"object_pos_start":[0.53992,0.00076,0.12038],"object_to_goal_dist_end":0.25331,"object_to_goal_dist_start":0.20335,"object_z_max":0.21196,"peak_contact_force":273004.11356,"phase_name":"retract_to_clearance","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":10092.0,"raw_peak_contact_force":1.94816,"subtask_id":"lift_object","tcp_end":[0.5237,0.00074,0.35582],"tcp_start":[0.52538,0.00079,0.13222],"tcp_to_object_dist_end":0.34141,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":478.0,"n_steps_budget":1000.0,"object_pos_end":[0.51449,0.03244,0.01602],"object_pos_start":[0.51449,0.03244,0.01602],"object_to_goal_dist_end":0.25331,"object_to_goal_dist_start":0.25331,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3967.0,"raw_peak_contact_force":0.12263,"subtask_id":"approach_goal","tcp_end":[0.63617,0.14405,0.35342],"tcp_start":[0.5237,0.00074,0.35582],"tcp_to_object_dist_end":0.37563,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":216.0,"n_steps_budget":1000.0,"object_pos_end":[0.51449,0.03244,0.01602],"object_pos_start":[0.51449,0.03244,0.01602],"object_to_goal_dist_end":0.25331,"object_to_goal_dist_start":0.25331,"object_z_max":0.01602,"peak_contact_force":273006.05362,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1781.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.64307,0.15458,0.22741],"tcp_start":[0.63617,0.14405,0.35342],"tcp_to_object_dist_end":0.27593,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51449,0.03244,0.01602],"object_pos_start":[0.51449,0.03244,0.01602],"object_to_goal_dist_end":0.25331,"object_to_goal_dist_start":0.25331,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.63807,0.15312,0.24479],"tcp_start":[0.64307,0.15458,0.22741],"tcp_to_object_dist_end":0.28666,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```