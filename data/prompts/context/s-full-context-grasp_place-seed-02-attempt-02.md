## Search State

- **Seed**: 2
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.0184 | 0.42 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | 0.0200 | 0.38 | ✅ accepted |
| 0 | align → align → pull → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | contact_detected | 0 | 0.1073 | 0.16 | ✅ accepted |

**Proposal policy**: task_score is 0.42 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.018) — your mutation base

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
      distance: 0.12
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
      - 0.08
      - 0.18
      default: 0.12
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
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
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
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.05
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
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.12, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **approach_above_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_goal_height: status=consumed; consumers=target.offset.z (replace)
    - approach_goal_speed: status=consumed; consumers=generator.speed (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: 0.018
- **task_score** (E): 0.417
- **fitness_score**: 0.688  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.670

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_object | 1.00 | 1.00 | 0.0774 |
| descend_to_grasp | 1.00 | 1.00 | 0.1960 |
| grasp | 1.00 | 1.00 | 0.0117 |
| lift | 1.00 | 1.00 | 0.1066 |
| approach_above_goal | 1.00 | 1.00 | 0.2681 |
| descend_to_place | 1.00 | 1.00 | 0.0939 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, -0.011, 0.230) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 13.145 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.493, -0.011, 0.230)→(0.488, -0.015, 0.035) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.488, -0.015, 0.035)→(0.480, -0.015, 0.026) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 44.667 | 0.136 | 0.191 |
| lift | lift | 1.00 / step_budget | (0.480, -0.015, 0.026)→(0.476, -0.015, 0.133) | (0.493, -0.015, 0.026)→(0.490, -0.015, 0.122) | 0.281→0.246 | 1.00 / 31.000 | 72.978 | 0.694 |
| approach_above_goal | approach | 1.00 / step_budget | (0.476, -0.015, 0.133)→(0.623, 0.161, 0.265) | (0.490, -0.015, 0.122)→(0.557, 0.085, 0.074) | 0.246→0.189 | 1.00 / 15.333 | 94253.354 | 1.378 |
| descend_to_place | descend | 1.00 / step_budget | (0.623, 0.161, 0.265)→(0.631, 0.172, 0.172) | (0.557, 0.085, 0.074)→(0.560, 0.089, 0.041) | 0.189→0.171 | 1.00 / 15.000 | 91002.321 | 0.174 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.858
- phase_score: 0.580
- phase_breakdown.approach_object_score: 0.297
- phase_breakdown.grasp_object_score: 0.795
- phase_breakdown.lift_object_score: 0.315
- phase_breakdown.approach_goal_score: 0.672
- phase_breakdown.place_object_score: 0.819
- grasp_place_fitness: 0.911

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.911
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.858
- **Median Q (composite search score)**: -0.081
- **K-run variance**: 0.0249
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.294


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.01266,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.13458,"approach_above_goal.approach_goal_speed":0.14978,"approach_above_goal.arc_height":0.05886,"approach_above_object.approach_height":0.17748,"approach_above_object.approach_speed":0.21807,"descend_to_grasp.descent_speed":0.12845,"descend_to_grasp.grasp_z_tolerance":0.01072,"descend_to_place.place_speed":0.06136,"descend_to_place.place_z_tolerance":0.00851,"lift.lift_height":0.1308,"lift.lift_speed":0.14107},"optimized_scores":{"best_composite_score":-0.10431,"best_fitness_score":0.56569,"best_task_score":0.16961},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2284.0,"contact_point_centroid":[0.49342,0.01238,-0.0025],"force_p95":0.15665,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.91659,"mean_force":0.14893,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.54765,0.07333,0.28936]},{"body_a":"world","body_b":"grasp_target","contact_count":138.0,"contact_point_centroid":[0.47348,-0.01917,-0.0011],"force_p95":0.52215,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72829,"mean_force":0.09833,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4628,-0.01949,0.029]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8543.0,"contact_point_centroid":[0.46242,-0.00042,0.07844],"force_p95":0.10476,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33162,"mean_force":0.06508,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46048,-0.01943,0.07617]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1705.0,"contact_point_centroid":[0.47122,0.0065,0.17095],"force_p95":0.18741,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33029,"mean_force":0.11221,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.46534,-0.01198,0.17152]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9234.0,"contact_point_centroid":[0.46245,-0.03835,0.077],"force_p95":0.10227,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31656,"mean_force":0.06108,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46047,-0.01943,0.0753]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1904.0,"contact_point_centroid":[0.47114,-0.03045,0.17003],"force_p95":0.1815,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30677,"mean_force":0.10479,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.46526,-0.0121,0.17104]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02,-0.00205],"force_p95":0.13899,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19058,"mean_force":0.12711,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46532,-0.01955,0.02825]},{"body_a":"world","body_b":"grasp_target","contact_count":584.0,"contact_point_centroid":[0.47616,-0.02015,-0.00178],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12346,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.49031,-0.00699,0.26476]},{"body_a":"world","body_b":"grasp_target","contact_count":2328.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47478,-0.01729,0.12922]},{"body_a":"world","body_b":"grasp_target","contact_count":1308.0,"contact_point_centroid":[0.49311,0.01281,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6215,0.15112,0.25682]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4821.0,"contact_point_centroid":[0.46425,-0.00031,0.02957],"force_p95":0.06778,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09551,"mean_force":0.04487,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4642,-0.01953,0.02716]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5165.0,"contact_point_centroid":[0.4641,-0.03875,0.02909],"force_p95":0.06659,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08149,"mean_force":0.04299,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46421,-0.01953,0.02716]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2260.0,"contact_point_centroid":[0.55202,0.07746,0.29533],"force_p95":0.01139,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01564,"mean_force":0.01059,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.55166,0.07746,0.29314]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1382.0,"contact_point_centroid":[0.62167,0.15111,0.25949],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01288,"mean_force":0.01054,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62148,0.1511,0.2571]}],"total_contact_groups":14},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.49311,0.01281,0.01602],"final_tcp_position":[0.62634,0.15652,0.19815],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273011.21472,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":147.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":39.18928,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":584.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48003,-0.01496,0.22625],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20033,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":582.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2328.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.47202,-0.01969,0.03491],"tcp_start":[0.48003,-0.01496,0.22625],"tcp_to_object_dist_end":0.00982,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01955,0.0258],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.2882,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13657,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11786.0,"raw_peak_contact_force":0.19058,"subtask_id":"grasp_object","tcp_end":[0.46418,-0.01952,0.02713],"tcp_start":[0.47202,-0.01969,0.03491],"tcp_to_object_dist_end":0.01193,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.47899,-0.01932,0.13285],"object_pos_start":[0.47603,-0.01955,0.0258],"object_to_goal_dist_end":0.2416,"object_to_goal_dist_start":0.2882,"object_z_max":0.1327,"peak_contact_force":218.85695,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17915.0,"raw_peak_contact_force":0.72829,"subtask_id":"lift_object","tcp_end":[0.46056,-0.01941,0.14408],"tcp_start":[0.46418,-0.01952,0.02713],"tcp_to_object_dist_end":0.02157,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":863.0,"n_steps_budget":1000.0,"object_pos_end":[0.49311,0.01281,0.01602],"object_pos_start":[0.47899,-0.01932,0.13285],"object_to_goal_dist_end":0.26614,"object_to_goal_dist_start":0.2416,"object_z_max":0.1817,"peak_contact_force":273011.21472,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8153.0,"raw_peak_contact_force":1.91659,"subtask_id":"approach_goal","tcp_end":[0.61827,0.14647,0.31718],"tcp_start":[0.46056,-0.01941,0.14408],"tcp_to_object_dist_end":0.35246,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":327.0,"n_steps_budget":1000.0,"object_pos_end":[0.49311,0.01281,0.01602],"object_pos_start":[0.49311,0.01281,0.01602],"object_to_goal_dist_end":0.26614,"object_to_goal_dist_start":0.26614,"object_z_max":0.01602,"peak_contact_force":273006.72695,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2690.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.62634,0.15652,0.19815],"tcp_start":[0.61827,0.14647,0.31718],"tcp_to_object_dist_end":0.26754,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58411,"average_solve_count":214.0,"average_success_count":214.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.10419,"approach_above_goal.approach_goal_speed":0.16917,"approach_above_goal.arc_height":0.06048,"approach_above_object.approach_height":0.19372,"approach_above_object.approach_speed":0.20643,"descend_to_grasp.descent_speed":0.11284,"descend_to_grasp.grasp_z_tolerance":0.00971,"descend_to_place.place_speed":0.03734,"descend_to_place.place_z_tolerance":0.01159,"lift.lift_height":0.10546,"lift.lift_speed":0.0369},"optimized_scores":{"best_composite_score":0.24094,"best_fitness_score":0.91094,"best_task_score":0.8585},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":160.0,"contact_point_centroid":[0.45372,-0.02484,-0.00122],"force_p95":0.50678,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60787,"mean_force":0.12574,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44582,-0.0254,0.02956]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4170.0,"contact_point_centroid":[0.62111,0.21701,0.16641],"force_p95":0.10112,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27698,"mean_force":0.06905,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6191,0.19844,0.16759]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3730.0,"contact_point_centroid":[0.62232,0.17958,0.16686],"force_p95":0.11632,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26448,"mean_force":0.07943,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61912,0.19847,0.16747]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19646.0,"contact_point_centroid":[0.44331,-0.0444,0.07942],"force_p95":0.0719,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25438,"mean_force":0.04902,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44332,-0.02529,0.07737]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18360.0,"contact_point_centroid":[0.44349,-0.00612,0.07755],"force_p95":0.07466,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24152,"mean_force":0.05172,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44333,-0.02529,0.07521]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11418.0,"contact_point_centroid":[0.51706,0.04723,0.19758],"force_p95":0.11317,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23574,"mean_force":0.07372,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.51428,0.06617,0.19671]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02616,-0.00208],"force_p95":0.14544,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22279,"mean_force":0.1289,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44839,-0.02549,0.02908]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12754.0,"contact_point_centroid":[0.51822,0.08559,0.19864],"force_p95":0.09775,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21175,"mean_force":0.06633,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.51489,0.06695,0.19759]},{"body_a":"world","body_b":"grasp_target","contact_count":540.0,"contact_point_centroid":[0.45856,-0.02632,-0.00177],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12353,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.48443,-0.00896,0.27116]},{"body_a":"world","body_b":"grasp_target","contact_count":2540.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46,-0.02244,0.13605]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5285.0,"contact_point_centroid":[0.4467,-0.0062,0.02959],"force_p95":0.06575,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10428,"mean_force":0.04114,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44731,-0.02545,0.02806]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5438.0,"contact_point_centroid":[0.4467,-0.04474,0.02945],"force_p95":0.06578,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08145,"mean_force":0.04117,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44731,-0.02545,0.02807]}],"total_contact_groups":12},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62789,0.20461,0.09163],"final_tcp_position":[0.62383,0.20445,0.12089],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.60787,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":136.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":540.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.46754,-0.01925,0.23963],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21392,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":635.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2540.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.45491,-0.02571,0.0353],"tcp_start":[0.46754,-0.01925,0.23963],"tcp_to_object_dist_end":0.00999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45845,-0.02554,0.02572],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.3032,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14248,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12523.0,"raw_peak_contact_force":0.22279,"subtask_id":"grasp_object","tcp_end":[0.44728,-0.02545,0.02804],"tcp_start":[0.45491,-0.02571,0.0353],"tcp_to_object_dist_end":0.01141,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":950.0,"n_steps_budget":1000.0,"object_pos_end":[0.45171,-0.02507,0.11557],"object_pos_start":[0.45845,-0.02554,0.02572],"object_to_goal_dist_end":0.2937,"object_to_goal_dist_start":0.3032,"object_z_max":0.11549,"peak_contact_force":0.07726,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38166.0,"raw_peak_contact_force":0.60787,"subtask_id":"lift_object","tcp_end":[0.44338,-0.02528,0.12434],"tcp_start":[0.44728,-0.02545,0.02804],"tcp_to_object_dist_end":0.01209,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":833.0,"n_steps_budget":1000.0,"object_pos_end":[0.61988,0.19372,0.18875],"object_pos_start":[0.45171,-0.02507,0.11557],"object_to_goal_dist_end":0.07671,"object_to_goal_dist_start":0.2937,"object_z_max":0.21096,"peak_contact_force":0.10902,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24172.0,"raw_peak_contact_force":0.23574,"subtask_id":"approach_goal","tcp_end":[0.61683,0.19368,0.2165],"tcp_start":[0.44338,-0.02528,0.12434],"tcp_to_object_dist_end":0.02792,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":280.0,"n_steps_budget":1000.0,"object_pos_end":[0.62789,0.20461,0.09163],"object_pos_start":[0.61988,0.19372,0.18875],"object_to_goal_dist_end":0.02289,"object_to_goal_dist_start":0.07671,"object_z_max":0.18875,"peak_contact_force":0.11472,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7900.0,"raw_peak_contact_force":0.27698,"subtask_id":"place_object","tcp_end":[0.62383,0.20445,0.12089],"tcp_start":[0.61683,0.19368,0.2165],"tcp_to_object_dist_end":0.02954,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.66851,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.07556,"approach_above_goal.approach_goal_speed":0.10745,"approach_above_goal.arc_height":0.0584,"approach_above_object.approach_height":0.18016,"approach_above_object.approach_speed":0.21428,"descend_to_grasp.descent_speed":0.09046,"descend_to_grasp.grasp_z_tolerance":0.01157,"descend_to_place.place_speed":0.04972,"descend_to_place.place_z_tolerance":0.01092,"lift.lift_height":0.14533,"lift.lift_speed":0.0649},"optimized_scores":{"best_composite_score":-0.08148,"best_fitness_score":0.58852,"best_task_score":0.2233},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1486.0,"contact_point_centroid":[0.5584,0.04932,-0.00271],"force_p95":0.33175,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.98239,"mean_force":0.16165,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.59427,0.092,0.25625]},{"body_a":"world","body_b":"grasp_target","contact_count":170.0,"contact_point_centroid":[0.53996,0.00071,-0.00111],"force_p95":0.50721,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74528,"mean_force":0.11524,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52796,0.00082,0.02554]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16780.0,"contact_point_centroid":[0.52705,-0.01821,0.07603],"force_p95":0.08904,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33221,"mean_force":0.06113,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52521,0.00078,0.07438]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17191.0,"contact_point_centroid":[0.52714,0.01976,0.07521],"force_p95":0.08796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32055,"mean_force":0.0599,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52524,0.00078,0.07371]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3661.0,"contact_point_centroid":[0.53395,-0.00773,0.16618],"force_p95":0.15561,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30866,"mean_force":0.0866,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.5303,0.01074,0.1682]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3525.0,"contact_point_centroid":[0.53471,0.03027,0.16858],"force_p95":0.15356,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29027,"mean_force":0.09039,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.53103,0.0117,0.17055]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00098,-0.00203],"force_p95":0.13177,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16046,"mean_force":0.1253,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53101,0.00088,0.02539]},{"body_a":"world","body_b":"grasp_target","contact_count":656.0,"contact_point_centroid":[0.54431,0.00113,-0.00181],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12337,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.51471,0.0004,0.26372]},{"body_a":"world","body_b":"grasp_target","contact_count":2340.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53372,0.00091,0.12804]},{"body_a":"world","body_b":"grasp_target","contact_count":740.0,"contact_point_centroid":[0.55797,0.04908,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63738,0.14835,0.22886]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53081,-0.01834,0.02665],"force_p95":0.07605,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1103,"mean_force":0.0517,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52976,0.00086,0.02396]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53074,0.01994,0.02577],"force_p95":0.06805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09672,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52976,0.00086,0.02396]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1382.0,"contact_point_centroid":[0.59931,0.09766,0.2611],"force_p95":0.01185,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01625,"mean_force":0.01067,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.59876,0.09765,0.25885]},{"body_a":"left_finger","body_b":"right_finger","contact_count":784.0,"contact_point_centroid":[0.63751,0.14835,0.23123],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.01051,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63737,0.14834,0.22892]}],"total_contact_groups":14},"final_pose_error":0.00977,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.55797,0.04908,0.01602],"final_tcp_position":[0.64156,0.15399,0.19757],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":9748.73706,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":165.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":656.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.5315,0.00083,0.22546],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19985,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":585.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2340.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.53846,0.00102,0.03403],"tcp_start":[0.5315,0.00083,0.22546],"tcp_to_object_dist_end":0.00992,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54415,0.00073,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12965,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.16046,"subtask_id":"grasp_object","tcp_end":[0.52973,0.00086,0.02393],"tcp_start":[0.53846,0.00102,0.03403],"tcp_to_object_dist_end":0.01456,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5398,0.00077,0.1189],"object_pos_start":[0.54415,0.00073,0.02588],"object_to_goal_dist_end":0.20393,"object_to_goal_dist_start":0.25053,"object_z_max":0.11879,"peak_contact_force":0.0,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":34141.0,"raw_peak_contact_force":0.74528,"subtask_id":"lift_object","tcp_end":[0.5254,0.00079,0.13031],"tcp_start":[0.52973,0.00086,0.02393],"tcp_to_object_dist_end":0.01837,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":782.0,"n_steps_budget":1000.0,"object_pos_end":[0.55797,0.04908,0.01602],"object_pos_start":[0.5398,0.00077,0.1189],"object_to_goal_dist_end":0.22489,"object_to_goal_dist_start":0.20393,"object_z_max":0.19055,"peak_contact_force":9748.73706,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10054.0,"raw_peak_contact_force":1.98239,"subtask_id":"approach_goal","tcp_end":[0.63511,0.14359,0.262],"tcp_start":[0.5254,0.00079,0.13031],"tcp_to_object_dist_end":0.27457,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":185.0,"n_steps_budget":1000.0,"object_pos_end":[0.55797,0.04908,0.01602],"object_pos_start":[0.55797,0.04908,0.01602],"object_to_goal_dist_end":0.22489,"object_to_goal_dist_start":0.22489,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1524.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.64156,0.15399,0.19757],"tcp_start":[0.63511,0.14359,0.262],"tcp_to_object_dist_end":0.22573,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```