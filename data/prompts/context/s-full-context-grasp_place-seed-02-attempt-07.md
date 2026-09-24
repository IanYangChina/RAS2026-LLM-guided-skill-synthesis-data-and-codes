## Search State

- **Seed**: 2
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.0234 | 0.33 | ❌ rejected |
| 6 | approach → descend → grasp → lift → retract → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 12 | -0.1916 | 0.16 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 12 | -0.0927 | 0.35 | ❌ rejected |
| 4 | approach → descend → grasp → lift → retract → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 14 | -0.3226 | 0.16 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.0684 | 0.52 | ✅ accepted |

**Proposal policy**: task_score is 0.33 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.023) — your mutation base

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

- **Composite score**: -0.023
- **task_score** (E): 0.333
- **fitness_score**: 0.647  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.670

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_object | 1.00 | 1.00 | 0.0652 |
| descend_to_grasp | 1.00 | 1.00 | 0.2086 |
| grasp | 1.00 | 1.00 | 0.0116 |
| lift | 0.67 | 1.00 | 0.1002 |
| approach_above_goal | 1.00 | 0.67 | 0.2582 |
| descend_to_place | 1.00 | 1.00 | 0.0644 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, -0.010, 0.243) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.495, -0.010, 0.243)→(0.489, -0.015, 0.035) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.489, -0.015, 0.035)→(0.480, -0.015, 0.026) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 44.667 | 0.137 | 0.194 |
| lift | lift | 0.67 / step_budget | (0.480, -0.015, 0.026)→(0.476, -0.015, 0.126) | (0.493, -0.015, 0.026)→(0.489, -0.015, 0.117) | 0.281→0.249 | 1.00 / 35.333 | 0.086 | 0.709 |
| approach_above_goal | approach | 1.00 / step_budget | (0.476, -0.015, 0.126)→(0.623, 0.161, 0.234) | (0.489, -0.015, 0.117)→(0.583, 0.112, 0.033) | 0.249→0.159 | 0.67 / 5.333 | 0.082 | 1.550 |
| descend_to_place | descend | 1.00 / step_budget | (0.623, 0.161, 0.234)→(0.630, 0.171, 0.171) | (0.583, 0.112, 0.033)→(0.583, 0.113, 0.016) | 0.159→0.175 | 1.00 / 8.000 | 3249.713 | 0.765 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.519
- phase_score: 0.586
- phase_breakdown.approach_object_score: 0.387
- phase_breakdown.grasp_object_score: 0.793
- phase_breakdown.lift_object_score: 0.361
- phase_breakdown.approach_goal_score: 0.567
- phase_breakdown.place_object_score: 0.821
- grasp_place_fitness: 0.741

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.741
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.519
- **Median Q (composite search score)**: -0.068
- **K-run variance**: 0.0045
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.386


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28631,"average_solve_count":241.0,"average_success_count":241.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.05002,"approach_above_goal.approach_goal_speed":0.03023,"approach_above_goal.arc_height":0.22363,"approach_above_object.approach_height":0.2309,"approach_above_object.approach_speed":0.15472,"descend_to_grasp.descent_speed":0.08376,"descend_to_grasp.grasp_z_tolerance":0.01747,"descend_to_place.place_speed":0.07017,"descend_to_place.place_z_tolerance":0.01376,"lift.lift_height":0.11443,"lift.lift_speed":0.14259},"optimized_scores":{"best_composite_score":-0.07348,"best_fitness_score":0.59652,"best_task_score":0.2305},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1114.0,"contact_point_centroid":[0.55379,0.04894,-0.00317],"force_p95":0.55128,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17226,"mean_force":0.17435,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.58285,0.11037,0.25917]},{"body_a":"world","body_b":"grasp_target","contact_count":138.0,"contact_point_centroid":[0.47319,-0.0191,-0.00122],"force_p95":0.52252,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.7344,"mean_force":0.11085,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46301,-0.01934,0.02859]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8640.0,"contact_point_centroid":[0.46239,-0.00025,0.07236],"force_p95":0.10399,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32716,"mean_force":0.06351,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46066,-0.01927,0.07011]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9324.0,"contact_point_centroid":[0.4624,-0.03822,0.07114],"force_p95":0.10133,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31616,"mean_force":0.05978,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46065,-0.01927,0.06946]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5805.0,"contact_point_centroid":[0.48634,0.0239,0.19693],"force_p95":0.14801,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22931,"mean_force":0.09559,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.48159,0.00551,0.19786]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6199.0,"contact_point_centroid":[0.4869,-0.01238,0.19668],"force_p95":0.13284,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22548,"mean_force":0.09162,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.482,0.00591,0.1977]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.01998,-0.00207],"force_p95":0.14275,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19983,"mean_force":0.12814,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46557,-0.0194,0.02817]},{"body_a":"world","body_b":"grasp_target","contact_count":260.0,"contact_point_centroid":[0.47616,-0.02015,-0.00151],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12474,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.49349,-0.00465,0.28929]},{"body_a":"world","body_b":"grasp_target","contact_count":3020.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12322,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47797,-0.01514,0.1536]},{"body_a":"world","body_b":"grasp_target","contact_count":592.0,"contact_point_centroid":[0.55361,0.04907,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61978,0.15014,0.21832]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4810.0,"contact_point_centroid":[0.46444,-0.00016,0.02938],"force_p95":0.06817,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10043,"mean_force":0.0449,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46445,-0.01937,0.02708]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5181.0,"contact_point_centroid":[0.4643,-0.03861,0.0289],"force_p95":0.06697,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08029,"mean_force":0.043,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46445,-0.01937,0.02708]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1019.0,"contact_point_centroid":[0.58769,0.11515,0.2606],"force_p95":0.01264,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01551,"mean_force":0.01082,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.58744,0.11514,0.25827]},{"body_a":"left_finger","body_b":"right_finger","contact_count":629.0,"contact_point_centroid":[0.62013,0.15011,0.22078],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.01048,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61974,0.15009,0.21859]}],"total_contact_groups":14},"final_pose_error":0.00981,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.55361,0.04907,0.01602],"final_tcp_position":[0.62436,0.15483,0.19524],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":2.17226,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":66.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02589],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28846,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12337,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":260.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48572,-0.01076,0.27559],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25006,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":755.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02589],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28846,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3020.0,"raw_peak_contact_force":0.12322,"subtask_id":"grasp_object","tcp_end":[0.47229,-0.01953,0.03485],"tcp_start":[0.48572,-0.01076,0.27559],"tcp_to_object_dist_end":0.00966,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01941,0.02576],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28814,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13968,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11791.0,"raw_peak_contact_force":0.19983,"subtask_id":"grasp_object","tcp_end":[0.46442,-0.01937,0.02705],"tcp_start":[0.47229,-0.01953,0.03485],"tcp_to_object_dist_end":0.01168,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":535.0,"n_steps_budget":600.0,"object_pos_end":[0.47878,-0.01918,0.11824],"object_pos_start":[0.47603,-0.01941,0.02576],"object_to_goal_dist_end":0.24549,"object_to_goal_dist_start":0.28814,"object_z_max":0.11811,"peak_contact_force":0.11549,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18102.0,"raw_peak_contact_force":0.7344,"subtask_id":"lift_object","tcp_end":[0.46065,-0.01926,0.12883],"tcp_start":[0.46442,-0.01937,0.02705],"tcp_to_object_dist_end":0.021,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":968.0,"n_steps_budget":1000.0,"object_pos_end":[0.55361,0.04907,0.01602],"object_pos_start":[0.47878,-0.01918,0.11824],"object_to_goal_dist_end":0.22013,"object_to_goal_dist_start":0.24549,"object_z_max":0.23193,"peak_contact_force":0.12263,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14137.0,"raw_peak_contact_force":2.17226,"subtask_id":"approach_goal","tcp_end":[0.61704,0.146,0.24235],"tcp_start":[0.46065,-0.01926,0.12883],"tcp_to_object_dist_end":0.25425,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":148.0,"n_steps_budget":1000.0,"object_pos_end":[0.55361,0.04907,0.01602],"object_pos_start":[0.55361,0.04907,0.01602],"object_to_goal_dist_end":0.22013,"object_to_goal_dist_start":0.22013,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1221.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.62436,0.15483,0.19524],"tcp_start":[0.61704,0.146,0.24235],"tcp_to_object_dist_end":0.21979,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41956,"average_solve_count":317.0,"average_success_count":317.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.06968,"approach_above_goal.approach_goal_speed":0.05684,"approach_above_goal.arc_height":0.09573,"approach_above_object.approach_height":0.17936,"approach_above_object.approach_speed":0.15179,"descend_to_grasp.descent_speed":0.03342,"descend_to_grasp.grasp_z_tolerance":0.01664,"descend_to_place.place_speed":0.09992,"descend_to_place.place_z_tolerance":0.01143,"lift.lift_height":0.1684,"lift.lift_speed":0.04748},"optimized_scores":{"best_composite_score":0.07124,"best_fitness_score":0.74124,"best_task_score":0.51937},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":755.0,"contact_point_centroid":[0.62598,0.21188,-0.00345],"force_p95":0.67572,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.04858,"mean_force":0.18956,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61932,0.19927,0.15277]},{"body_a":"world","body_b":"grasp_target","contact_count":156.0,"contact_point_centroid":[0.45449,-0.02484,-0.00119],"force_p95":0.49501,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6536,"mean_force":0.10384,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44569,-0.02541,0.02965]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12601.0,"contact_point_centroid":[0.49823,0.0242,0.20555],"force_p95":0.13178,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2757,"mean_force":0.0724,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.49519,0.04281,0.20608]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20809.0,"contact_point_centroid":[0.44309,-0.04445,0.08056],"force_p95":0.07123,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27467,"mean_force":0.04907,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44324,-0.02531,0.07883]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20427.0,"contact_point_centroid":[0.44314,-0.00613,0.08206],"force_p95":0.07182,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26142,"mean_force":0.04943,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44325,-0.02531,0.07999]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11913.0,"contact_point_centroid":[0.50267,0.06676,0.20745],"force_p95":0.12686,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25237,"mean_force":0.07646,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.49947,0.04811,0.20769]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02616,-0.00208],"force_p95":0.14523,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22231,"mean_force":0.12882,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44829,-0.0255,0.02905]},{"body_a":"world","body_b":"grasp_target","contact_count":624.0,"contact_point_centroid":[0.45856,-0.02632,-0.0018],"force_p95":0.13787,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12341,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.48377,-0.00937,0.26461]},{"body_a":"world","body_b":"grasp_target","contact_count":2668.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45923,-0.02279,0.12972]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5286.0,"contact_point_centroid":[0.44662,-0.00622,0.02964],"force_p95":0.06572,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1038,"mean_force":0.04114,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44721,-0.02546,0.02803]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5437.0,"contact_point_centroid":[0.44662,-0.04476,0.0295],"force_p95":0.06583,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0813,"mean_force":0.04116,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44721,-0.02546,0.02804]},{"body_a":"left_finger","body_b":"right_finger","contact_count":554.0,"contact_point_centroid":[0.62077,0.20061,0.14468],"force_p95":0.0139,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01636,"mean_force":0.01108,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62038,0.20059,0.14265]}],"total_contact_groups":12},"final_pose_error":0.00987,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62584,0.21211,0.01602],"final_tcp_position":[0.62345,0.20415,0.12014],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":2.04858,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":157.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":624.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.46635,-0.01998,0.22645],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20068,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":667.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2668.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.4548,-0.02572,0.03526],"tcp_start":[0.46635,-0.01998,0.22645],"tcp_to_object_dist_end":0.01,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45845,-0.02555,0.02572],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30321,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14232,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12523.0,"raw_peak_contact_force":0.22231,"subtask_id":"grasp_object","tcp_end":[0.44718,-0.02546,0.02801],"tcp_start":[0.4548,-0.02572,0.03526],"tcp_to_object_dist_end":0.01149,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4519,-0.0253,0.12171],"object_pos_start":[0.45845,-0.02555,0.02572],"object_to_goal_dist_end":0.29385,"object_to_goal_dist_start":0.30321,"object_z_max":0.12161,"peak_contact_force":0.07065,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41392.0,"raw_peak_contact_force":0.6536,"subtask_id":"lift_object","tcp_end":[0.4433,-0.0253,0.13148],"tcp_start":[0.44718,-0.02546,0.02801],"tcp_to_object_dist_end":0.01302,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62718,0.20919,0.0661],"object_pos_start":[0.4519,-0.0253,0.12171],"object_to_goal_dist_end":0.04812,"object_to_goal_dist_start":0.29385,"object_z_max":0.22938,"peak_contact_force":0.0,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24514.0,"raw_peak_contact_force":0.2757,"subtask_id":"approach_goal","tcp_end":[0.61718,0.1946,0.1928],"tcp_start":[0.4433,-0.0253,0.13148],"tcp_to_object_dist_end":0.12794,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":204.0,"n_steps_budget":1000.0,"object_pos_end":[0.62584,0.21211,0.01602],"object_pos_start":[0.62718,0.20919,0.0661],"object_to_goal_dist_end":0.09827,"object_to_goal_dist_start":0.04812,"object_z_max":0.0661,"peak_contact_force":0.12266,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1309.0,"raw_peak_contact_force":2.04858,"subtask_id":"place_object","tcp_end":[0.62345,0.20415,0.12014],"tcp_start":[0.61718,0.1946,0.1928],"tcp_to_object_dist_end":0.10445,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41905,"average_solve_count":210.0,"average_success_count":210.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.08108,"approach_above_goal.approach_goal_speed":0.08435,"approach_above_goal.arc_height":0.22915,"approach_above_object.approach_height":0.18158,"approach_above_object.approach_speed":0.18758,"descend_to_grasp.descent_speed":0.05759,"descend_to_grasp.grasp_z_tolerance":0.01081,"descend_to_place.place_speed":0.09128,"descend_to_place.place_z_tolerance":0.01557,"lift.lift_height":0.14272,"lift.lift_speed":0.05859},"optimized_scores":{"best_composite_score":-0.068,"best_fitness_score":0.602,"best_task_score":0.25024},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1197.0,"contact_point_centroid":[0.56963,0.07805,-0.00299],"force_p95":0.50098,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.20093,"mean_force":0.16998,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.60206,0.10199,0.26816]},{"body_a":"world","body_b":"grasp_target","contact_count":206.0,"contact_point_centroid":[0.53875,0.0007,-0.00113],"force_p95":0.48709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73941,"mean_force":0.11812,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52774,0.00082,0.02541]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18655.0,"contact_point_centroid":[0.52616,-0.01832,0.07392],"force_p95":0.07817,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3291,"mean_force":0.0547,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52522,0.00078,0.07195]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19150.0,"contact_point_centroid":[0.52615,0.01986,0.07269],"force_p95":0.07753,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31558,"mean_force":0.05365,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52524,0.00078,0.07087]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6181.0,"contact_point_centroid":[0.53468,0.03145,0.17664],"force_p95":0.14642,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28241,"mean_force":0.07823,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.53156,0.01267,0.17713]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6407.0,"contact_point_centroid":[0.53383,-0.00696,0.17443],"force_p95":0.14523,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27987,"mean_force":0.07543,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.5308,0.01172,0.1751]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00098,-0.00203],"force_p95":0.13175,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16045,"mean_force":0.1253,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53103,0.00088,0.02527]},{"body_a":"world","body_b":"grasp_target","contact_count":648.0,"contact_point_centroid":[0.54431,0.00113,-0.0018],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12338,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.51474,0.0004,0.26428]},{"body_a":"world","body_b":"grasp_target","contact_count":2524.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53361,0.00091,0.12846]},{"body_a":"world","body_b":"grasp_target","contact_count":764.0,"contact_point_centroid":[0.56936,0.07808,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63739,0.14858,0.23263]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53082,-0.01834,0.02653],"force_p95":0.07605,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11017,"mean_force":0.0517,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52978,0.00086,0.02384]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53075,0.01994,0.02565],"force_p95":0.06805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09672,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52978,0.00086,0.02384]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1086.0,"contact_point_centroid":[0.60732,0.10812,0.27185],"force_p95":0.01259,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01638,"mean_force":0.01068,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.60692,0.10811,0.26962]},{"body_a":"left_finger","body_b":"right_finger","contact_count":823.0,"contact_point_centroid":[0.638,0.14861,0.23475],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01275,"mean_force":0.01035,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6374,0.14859,0.23252]}],"total_contact_groups":14},"final_pose_error":0.00973,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.56936,0.07808,0.01602],"final_tcp_position":[0.64171,0.15418,0.19776],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":9748.89398,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":163.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":648.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53145,0.00083,0.22669],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20109,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":631.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2524.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.53847,0.00102,0.03389],"tcp_start":[0.53145,0.00083,0.22669],"tcp_to_object_dist_end":0.0098,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54415,0.00073,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12963,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.16045,"subtask_id":"grasp_object","tcp_end":[0.52975,0.00086,0.02381],"tcp_start":[0.53847,0.00102,0.03389],"tcp_to_object_dist_end":0.01455,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53684,0.00079,0.11023],"object_pos_start":[0.54415,0.00073,0.02588],"object_to_goal_dist_end":0.2087,"object_to_goal_dist_start":0.25053,"object_z_max":0.11013,"peak_contact_force":0.07312,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38011.0,"raw_peak_contact_force":0.73941,"subtask_id":"lift_object","tcp_end":[0.52535,0.00079,0.11895],"tcp_start":[0.52975,0.00086,0.02381],"tcp_to_object_dist_end":0.01442,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":874.0,"n_steps_budget":1000.0,"object_pos_end":[0.56936,0.07808,0.01602],"object_pos_start":[0.53684,0.00079,0.11023],"object_to_goal_dist_end":0.2078,"object_to_goal_dist_start":0.2087,"object_z_max":0.21746,"peak_contact_force":0.12263,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14871.0,"raw_peak_contact_force":2.20093,"subtask_id":"approach_goal","tcp_end":[0.6348,0.14361,0.26767],"tcp_start":[0.52535,0.00079,0.11895],"tcp_to_object_dist_end":0.26815,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":191.0,"n_steps_budget":1000.0,"object_pos_end":[0.56936,0.07808,0.01602],"object_pos_start":[0.56936,0.07808,0.01602],"object_to_goal_dist_end":0.2078,"object_to_goal_dist_start":0.2078,"object_z_max":0.01602,"peak_contact_force":9748.89398,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1587.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.64171,0.15418,0.19776],"tcp_start":[0.6348,0.14361,0.26767],"tcp_to_object_dist_end":0.20989,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```