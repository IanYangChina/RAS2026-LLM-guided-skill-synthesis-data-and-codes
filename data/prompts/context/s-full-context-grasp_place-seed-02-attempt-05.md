## Search State

- **Seed**: 2
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 12 | -0.0927 | 0.35 | ❌ rejected |
| 4 | approach → descend → grasp → lift → retract → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 14 | -0.3226 | 0.16 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.0684 | 0.52 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.0184 | 0.42 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | 0.0200 | 0.38 | ✅ accepted |

**Proposal policy**: task_score is 0.35 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.093) — your mutation base

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

- **Composite score**: -0.093
- **task_score** (E): 0.355
- **fitness_score**: 0.657  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.750

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_object | 1.00 | 1.00 | 0.0549 |
| descend_to_grasp | 1.00 | 1.00 | 0.2200 |
| grasp | 1.00 | 1.00 | 0.0117 |
| lift | 0.33 | 1.00 | 0.0981 |
| approach_above_goal | 1.00 | 1.00 | 0.2593 |
| descend_to_place | 1.00 | 0.67 | 0.0928 |
| release | 1.00 | 1.00 | 0.0198 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, -0.010, 0.254) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 14.591 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.493, -0.010, 0.254)→(0.489, -0.015, 0.035) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.124 |
| grasp | grasp | 1.00 / step_budget | (0.489, -0.015, 0.035)→(0.480, -0.015, 0.026) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 45.000 | 0.137 | 0.198 |
| lift | lift | 0.33 / step_budget | (0.480, -0.015, 0.026)→(0.476, -0.015, 0.124) | (0.493, -0.015, 0.026)→(0.486, -0.015, 0.115) | 0.281→0.252 | 1.00 / 38.000 | 0.083 | 0.654 |
| approach_above_goal | approach | 1.00 / step_budget | (0.476, -0.015, 0.124)→(0.616, 0.153, 0.261) | (0.486, -0.015, 0.115)→(0.596, 0.128, 0.164) | 0.252→0.134 | 1.00 / 19.000 | 91004.755 | 0.776 |
| descend_to_place | descend | 1.00 / step_budget | (0.616, 0.153, 0.261)→(0.630, 0.171, 0.171) | (0.596, 0.128, 0.164)→(0.604, 0.144, 0.084) | 0.134→0.096 | 0.67 / 9.333 | 0.084 | 0.261 |
| release | release | 1.00 / step_budget | (0.630, 0.171, 0.171)→(0.624, 0.169, 0.189) | (0.604, 0.144, 0.084)→(0.603, 0.146, 0.016) | 0.096→0.164 | 1.00 / 4.000 | 0.120 | 1.069 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.520
- phase_score: 0.442
- phase_breakdown.transport_score: 0.359
- phase_breakdown.approach_object_score: 0.575
- phase_breakdown.grasp_object_score: 0.794
- phase_breakdown.lift_object_score: 0.030
- phase_breakdown.place_object_score: 0.564
- grasp_place_fitness: 0.742

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.742
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.520
- **Median Q (composite search score)**: -0.112
- **K-run variance**: 0.0039
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.389


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24653,"average_solve_count":288.0,"average_success_count":288.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.0668,"approach_above_goal.approach_goal_speed":0.03308,"approach_above_goal.arc_height":0.09368,"approach_above_object.approach_height":0.24159,"approach_above_object.approach_speed":0.12904,"descend_to_grasp.descent_speed":0.10277,"descend_to_grasp.grasp_z_tolerance":0.01156,"descend_to_place.place_speed":0.03712,"descend_to_place.place_z_tolerance":0.01308,"lift.lift_height":0.15102,"lift.lift_speed":0.04002,"release.release_duration":0.47593},"optimized_scores":{"best_composite_score":-0.11226,"best_fitness_score":0.63774,"best_task_score":0.31263},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":611.0,"contact_point_centroid":[0.629,0.17046,-0.00373],"force_p95":0.80849,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.9048,"mean_force":0.20245,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61918,0.15308,0.19551]},{"body_a":"world","body_b":"grasp_target","contact_count":165.0,"contact_point_centroid":[0.471,-0.01879,-0.00119],"force_p95":0.4727,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63547,"mean_force":0.12669,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46302,-0.01928,0.0288]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1738.0,"contact_point_centroid":[0.61708,0.12606,0.23042],"force_p95":0.17225,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4205,"mean_force":0.10563,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61395,0.14404,0.23493]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2071.0,"contact_point_centroid":[0.61747,0.16232,0.22841],"force_p95":0.15363,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38418,"mean_force":0.09776,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61448,0.14456,0.23306]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19484.0,"contact_point_centroid":[0.46043,-1e-05,0.07539],"force_p95":0.07494,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2677,"mean_force":0.05151,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46048,-0.0192,0.07313]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21109.0,"contact_point_centroid":[0.46031,-0.0383,0.07727],"force_p95":0.07105,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26557,"mean_force":0.04825,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46047,-0.0192,0.07532]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15987.0,"contact_point_centroid":[0.50329,0.00688,0.2236],"force_p95":0.10446,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22301,"mean_force":0.06253,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.50102,0.02574,0.22318]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.01996,-0.00208],"force_p95":0.14532,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22274,"mean_force":0.12886,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4657,-0.01933,0.02836]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15100.0,"contact_point_centroid":[0.50562,0.04689,0.22667],"force_p95":0.1019,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.217,"mean_force":0.06523,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.50316,0.02795,0.22572]},{"body_a":"world","body_b":"grasp_target","contact_count":204.0,"contact_point_centroid":[0.47616,-0.02015,-0.00136],"force_p95":0.13839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12472,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.49437,-0.00385,0.29323]},{"body_a":"world","body_b":"grasp_target","contact_count":3052.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12666,"mean_force":0.12265,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47882,-0.0144,0.15771]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4808.0,"contact_point_centroid":[0.46454,-7e-05,0.0295],"force_p95":0.06842,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10249,"mean_force":0.04496,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46459,-0.01931,0.02726]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5436.0,"contact_point_centroid":[0.46403,-0.03855,0.02891],"force_p95":0.06544,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08181,"mean_force":0.04112,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46459,-0.01931,0.02726]}],"total_contact_groups":13},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62881,0.17065,0.016],"final_tcp_position":[0.62404,0.15439,0.19469],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.9048,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":52.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02587],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28847,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12703,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":204.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48736,-0.00935,0.28376],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25836,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":763.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02587],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28847,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3052.0,"raw_peak_contact_force":0.12666,"subtask_id":"grasp_object","tcp_end":[0.47243,-0.01947,0.03504],"tcp_start":[0.48736,-0.00935,0.28376],"tcp_to_object_dist_end":0.00979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47604,-0.01934,0.02573],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28811,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14162,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12044.0,"raw_peak_contact_force":0.22274,"subtask_id":"grasp_object","tcp_end":[0.46456,-0.01931,0.02723],"tcp_start":[0.47243,-0.01947,0.03504],"tcp_to_object_dist_end":0.01158,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46898,-0.01909,0.11357],"object_pos_start":[0.47604,-0.01934,0.02573],"object_to_goal_dist_end":0.25301,"object_to_goal_dist_start":0.28811,"object_z_max":0.11347,"peak_contact_force":0.07697,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40758.0,"raw_peak_contact_force":0.63547,"subtask_id":"lift_object","tcp_end":[0.46052,-0.01919,0.12224],"tcp_start":[0.46456,-0.01931,0.02723],"tcp_to_object_dist_end":0.01211,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61951,0.13764,0.24617],"object_pos_start":[0.46898,-0.01909,0.11357],"object_to_goal_dist_end":0.06132,"object_to_goal_dist_start":0.25301,"object_z_max":0.26619,"peak_contact_force":0.15283,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31087.0,"raw_peak_contact_force":0.22301,"subtask_id":"transport","tcp_end":[0.60919,0.13762,0.26593],"tcp_start":[0.46052,-0.01919,0.12224],"tcp_to_object_dist_end":0.02229,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":240.0,"n_steps_budget":1000.0,"object_pos_end":[0.63114,0.1629,0.1394],"object_pos_start":[0.61951,0.13764,0.24617],"object_to_goal_dist_end":0.05075,"object_to_goal_dist_start":0.06132,"object_z_max":0.24617,"peak_contact_force":0.0,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3809.0,"raw_peak_contact_force":0.4205,"subtask_id":"place_object","tcp_end":[0.62404,0.15439,0.19469],"tcp_start":[0.60919,0.13762,0.26593],"tcp_to_object_dist_end":0.05638,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62881,0.17065,0.016],"object_pos_start":[0.63114,0.1629,0.1394],"object_to_goal_dist_end":0.17441,"object_to_goal_dist_start":0.05075,"object_z_max":0.1394,"peak_contact_force":0.12308,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":611.0,"raw_peak_contact_force":1.9048,"subtask_id":"place_object","tcp_end":[0.61853,0.15286,0.2139],"tcp_start":[0.62404,0.15439,0.19469],"tcp_to_object_dist_end":0.19896,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34915,"average_solve_count":295.0,"average_success_count":295.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.12452,"approach_above_goal.approach_goal_speed":0.05015,"approach_above_goal.arc_height":0.08007,"approach_above_object.approach_height":0.15823,"approach_above_object.approach_speed":0.24952,"descend_to_grasp.descent_speed":0.0942,"descend_to_grasp.grasp_z_tolerance":0.01009,"descend_to_place.place_speed":0.04917,"descend_to_place.place_z_tolerance":0.01729,"lift.lift_height":0.16033,"lift.lift_speed":0.03607,"release.release_duration":0.61219},"optimized_scores":{"best_composite_score":-0.00823,"best_fitness_score":0.74177,"best_task_score":0.5203},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":305.0,"contact_point_centroid":[0.62436,0.20248,-0.00418],"force_p95":0.72562,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.17994,"mean_force":0.22649,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61625,0.20121,0.12686]},{"body_a":"world","body_b":"grasp_target","contact_count":160.0,"contact_point_centroid":[0.45371,-0.02485,-0.00122],"force_p95":0.51922,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60354,"mean_force":0.12612,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44576,-0.02544,0.02949]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":627.0,"contact_point_centroid":[0.62449,0.22118,0.10993],"force_p95":0.12854,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.47297,"mean_force":0.08081,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62079,0.20292,0.11482]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":517.0,"contact_point_centroid":[0.62559,0.18469,0.11039],"force_p95":0.12729,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43949,"mean_force":0.09531,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62081,0.20292,0.11484]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20788.0,"contact_point_centroid":[0.44321,-0.04443,0.0821],"force_p95":0.07165,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25391,"mean_force":0.04877,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44327,-0.02533,0.08005]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19222.0,"contact_point_centroid":[0.44343,-0.00615,0.08001],"force_p95":0.07472,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24131,"mean_force":0.05195,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44327,-0.02533,0.07762]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4321.0,"contact_point_centroid":[0.61608,0.20882,0.18041],"force_p95":0.14066,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24095,"mean_force":0.09156,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61265,0.19054,0.18383]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4385.0,"contact_point_centroid":[0.61584,0.17212,0.18152],"force_p95":0.13724,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21918,"mean_force":0.08837,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6125,0.19034,0.18487]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02616,-0.00207],"force_p95":0.14392,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21129,"mean_force":0.12849,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44832,-0.02553,0.02904]},{"body_a":"world","body_b":"grasp_target","contact_count":748.0,"contact_point_centroid":[0.45856,-0.02632,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12328,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.4828,-0.00988,0.25462]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15652.0,"contact_point_centroid":[0.50792,0.07456,0.22233],"force_p95":0.08869,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13652,"mean_force":0.06246,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.50556,0.05557,0.22106]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16711.0,"contact_point_centroid":[0.50383,0.0319,0.2187],"force_p95":0.08765,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13488,"mean_force":0.05921,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.50171,0.0508,0.21805]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5286.0,"contact_point_centroid":[0.44664,-0.00624,0.0296],"force_p95":0.06556,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12989,"mean_force":0.04114,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44724,-0.02549,0.02802]},{"body_a":"world","body_b":"grasp_target","contact_count":2192.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45849,-0.02324,0.11984]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5434.0,"contact_point_centroid":[0.44665,-0.04478,0.02945],"force_p95":0.06565,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08081,"mean_force":0.04118,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44725,-0.02549,0.02802]}],"total_contact_groups":15},"final_pose_error":0.00989,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.6263,0.20262,0.01635],"final_tcp_position":[0.62313,0.2036,0.11936],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":43.52524,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":188.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":43.52524,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":748.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.46466,-0.02085,0.20639],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18056,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":548.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2192.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.45485,-0.02575,0.03525],"tcp_start":[0.46466,-0.02085,0.20639],"tcp_to_object_dist_end":0.00997,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02557,0.02574],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30322,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14118,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12520.0,"raw_peak_contact_force":0.21129,"subtask_id":"grasp_object","tcp_end":[0.44722,-0.02549,0.02799],"tcp_start":[0.45485,-0.02575,0.03525],"tcp_to_object_dist_end":0.01145,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45139,-0.0251,0.1204],"object_pos_start":[0.45844,-0.02557,0.02574],"object_to_goal_dist_end":0.29398,"object_to_goal_dist_start":0.30322,"object_z_max":0.1203,"peak_contact_force":0.07798,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40170.0,"raw_peak_contact_force":0.60354,"subtask_id":"lift_object","tcp_end":[0.44332,-0.02532,0.12948],"tcp_start":[0.44722,-0.02549,0.02799],"tcp_to_object_dist_end":0.01215,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61499,0.17935,0.2303],"object_pos_start":[0.45139,-0.0251,0.1204],"object_to_goal_dist_end":0.12066,"object_to_goal_dist_start":0.29398,"object_z_max":0.24739,"peak_contact_force":0.13652,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32363.0,"raw_peak_contact_force":0.13652,"subtask_id":"transport","tcp_end":[0.60527,0.17927,0.24837],"tcp_start":[0.44332,-0.02532,0.12948],"tcp_to_object_dist_end":0.02052,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":410.0,"n_steps_budget":1000.0,"object_pos_end":[0.62909,0.20354,0.09572],"object_pos_start":[0.61499,0.17935,0.2303],"object_to_goal_dist_end":0.01901,"object_to_goal_dist_start":0.12066,"object_z_max":0.2303,"peak_contact_force":0.12927,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8706.0,"raw_peak_contact_force":0.24095,"subtask_id":"place_object","tcp_end":[0.62313,0.2036,0.11936],"tcp_start":[0.60527,0.17927,0.24837],"tcp_to_object_dist_end":0.02437,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.6263,0.20262,0.01635],"object_pos_start":[0.62909,0.20354,0.09572],"object_to_goal_dist_end":0.098,"object_to_goal_dist_start":0.01901,"object_z_max":0.09572,"peak_contact_force":0.11544,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1449.0,"raw_peak_contact_force":1.17994,"subtask_id":"place_object","tcp_end":[0.61615,0.20117,0.13812],"tcp_start":[0.62313,0.2036,0.11936],"tcp_to_object_dist_end":0.1222,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57872,"average_solve_count":235.0,"average_success_count":235.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.07498,"approach_above_goal.approach_goal_speed":0.05995,"approach_above_goal.arc_height":0.09374,"approach_above_object.approach_height":0.2341,"approach_above_object.approach_speed":0.13902,"descend_to_grasp.descent_speed":0.08685,"descend_to_grasp.grasp_z_tolerance":0.01982,"descend_to_place.place_speed":0.04747,"descend_to_place.place_z_tolerance":0.01594,"lift.lift_height":0.11352,"lift.lift_speed":0.05982,"release.release_duration":0.49682},"optimized_scores":{"best_composite_score":-0.15755,"best_fitness_score":0.59245,"best_task_score":0.23151},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1427.0,"contact_point_centroid":[0.55307,0.06579,-0.00283],"force_p95":0.40386,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.96832,"mean_force":0.16347,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.59446,0.09202,0.27999]},{"body_a":"world","body_b":"grasp_target","contact_count":200.0,"contact_point_centroid":[0.53937,0.0007,-0.00114],"force_p95":0.48407,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72157,"mean_force":0.11363,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52765,0.00082,0.02538]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17947.0,"contact_point_centroid":[0.52616,-0.01831,0.0735],"force_p95":0.08141,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32034,"mean_force":0.05712,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5251,0.00078,0.07153]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18894.0,"contact_point_centroid":[0.5262,0.01981,0.07348],"force_p95":0.07788,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31111,"mean_force":0.05445,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52513,0.00078,0.07171]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6394.0,"contact_point_centroid":[0.52548,-0.01705,0.18253],"force_p95":0.14367,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2913,"mean_force":0.07779,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.52279,0.00169,0.18323]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6818.0,"contact_point_centroid":[0.52563,0.0205,0.17987],"force_p95":0.14378,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26807,"mean_force":0.07408,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.52294,0.00182,0.18051]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00098,-0.00203],"force_p95":0.13178,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16077,"mean_force":0.1253,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5309,0.00088,0.02525]},{"body_a":"world","body_b":"grasp_target","contact_count":368.0,"contact_point_centroid":[0.54431,0.00113,-0.00166],"force_p95":0.13823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12404,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.51205,0.00033,0.28723]},{"body_a":"world","body_b":"grasp_target","contact_count":2928.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.5312,0.00084,0.15116]},{"body_a":"world","body_b":"grasp_target","contact_count":816.0,"contact_point_centroid":[0.55286,0.06572,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63712,0.14837,0.23228]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55286,0.06572,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63755,0.15305,0.19683]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53074,-0.01834,0.0265],"force_p95":0.07605,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11015,"mean_force":0.05169,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52965,0.00086,0.02382]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53066,0.01994,0.02562],"force_p95":0.06806,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09682,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52965,0.00086,0.02382]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1349.0,"contact_point_centroid":[0.59916,0.09744,0.28319],"force_p95":0.01242,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01519,"mean_force":0.01064,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.59872,0.09743,0.28087]},{"body_a":"left_finger","body_b":"right_finger","contact_count":888.0,"contact_point_centroid":[0.63778,0.14841,0.23441],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01266,"mean_force":0.01026,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63713,0.14839,0.23213]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.64043,0.15383,0.19581],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01265,"mean_force":0.01005,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63999,0.15381,0.1936]}],"total_contact_groups":16},"final_pose_error":0.00975,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.55286,0.06572,0.01602],"final_tcp_position":[0.64161,0.15411,0.19767],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273013.9761,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":93.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.026],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25013,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12213,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":368.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52624,0.00069,0.27263],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.24729,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":732.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.026],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25013,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2928.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.53835,0.00102,0.03387],"tcp_start":[0.52624,0.00069,0.27263],"tcp_to_object_dist_end":0.00986,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54415,0.00072,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12965,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.16077,"subtask_id":"grasp_object","tcp_end":[0.52962,0.00086,0.02378],"tcp_start":[0.53835,0.00102,0.03387],"tcp_to_object_dist_end":0.01468,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53685,0.00054,0.11192],"object_pos_start":[0.54415,0.00072,0.02588],"object_to_goal_dist_end":0.20823,"object_to_goal_dist_start":0.25053,"object_z_max":0.11181,"peak_contact_force":0.09331,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37041.0,"raw_peak_contact_force":0.72157,"subtask_id":"lift_object","tcp_end":[0.52525,0.00079,0.1214],"tcp_start":[0.52962,0.00086,0.02378],"tcp_to_object_dist_end":0.01498,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":950.0,"n_steps_budget":1000.0,"object_pos_end":[0.55286,0.06572,0.01602],"object_pos_start":[0.53685,0.00054,0.11192],"object_to_goal_dist_end":0.21947,"object_to_goal_dist_start":0.20823,"object_z_max":0.22856,"peak_contact_force":273013.9761,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15988.0,"raw_peak_contact_force":1.96832,"subtask_id":"transport","tcp_end":[0.63462,0.14333,0.26778],"tcp_start":[0.52525,0.00079,0.1214],"tcp_to_object_dist_end":0.27585,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":204.0,"n_steps_budget":1000.0,"object_pos_end":[0.55286,0.06572,0.01602],"object_pos_start":[0.55286,0.06572,0.01602],"object_to_goal_dist_end":0.21947,"object_to_goal_dist_start":0.21947,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1704.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.64161,0.15411,0.19767],"tcp_start":[0.63462,0.14333,0.26778],"tcp_to_object_dist_end":0.22065,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55286,0.06572,0.01602],"object_pos_start":[0.55286,0.06572,0.01602],"object_to_goal_dist_end":0.21947,"object_to_goal_dist_start":0.21947,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.63613,0.15259,0.21602],"tcp_start":[0.64161,0.15411,0.19767],"tcp_to_object_dist_end":0.23341,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```