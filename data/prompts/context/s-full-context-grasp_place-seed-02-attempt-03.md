## Search State

- **Seed**: 2
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.0684 | 0.52 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.0184 | 0.42 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | 0.0200 | 0.38 | ✅ accepted |
| 0 | align → align → pull → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | contact_detected | 0 | 0.1073 | 0.16 | ✅ accepted |

**Proposal policy**: task_score is 0.52 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.068) — your mutation base

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

- **Composite score**: 0.068
- **task_score** (E): 0.517
- **fitness_score**: 0.738  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.670

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_object | 1.00 | 1.00 | 0.0698 |
| descend_to_grasp | 1.00 | 1.00 | 0.2039 |
| grasp | 1.00 | 1.00 | 0.0117 |
| lift | 0.67 | 1.00 | 0.0975 |
| approach_above_goal | 1.00 | 1.00 | 0.2564 |
| descend_to_place | 1.00 | 1.00 | 0.0572 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.492, -0.011, 0.238) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.122 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.492, -0.011, 0.238)→(0.488, -0.015, 0.035) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.488, -0.015, 0.035)→(0.480, -0.015, 0.026) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 44.667 | 0.136 | 0.188 |
| lift | lift | 0.67 / step_budget | (0.480, -0.015, 0.026)→(0.476, -0.015, 0.124) | (0.493, -0.015, 0.026)→(0.486, -0.015, 0.115) | 0.281→0.252 | 1.00 / 39.667 | 0.076 | 0.632 |
| approach_above_goal | approach | 1.00 / step_budget | (0.476, -0.015, 0.124)→(0.623, 0.161, 0.227) | (0.486, -0.015, 0.115)→(0.594, 0.133, 0.063) | 0.252→0.144 | 1.00 / 14.000 | 0.113 | 1.557 |
| descend_to_place | descend | 1.00 / step_budget | (0.623, 0.161, 0.227)→(0.630, 0.171, 0.171) | (0.594, 0.133, 0.063)→(0.596, 0.136, 0.044) | 0.144→0.134 | 1.00 / 12.333 | 0.132 | 0.201 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.184
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.612
- phase_breakdown.approach_object_score: 0.682
- phase_breakdown.grasp_object_score: 0.793
- phase_breakdown.lift_object_score: 0.341
- phase_breakdown.approach_goal_score: 0.423
- phase_breakdown.place_object_score: 0.821
- grasp_place_fitness: 0.982

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.982
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: -0.047
- **K-run variance**: 0.0296
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.419


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70286,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.05137,"approach_above_goal.approach_goal_speed":0.13994,"approach_above_goal.arc_height":0.24912,"approach_above_object.approach_height":0.20889,"approach_above_object.approach_speed":0.14536,"descend_to_grasp.descent_speed":0.12948,"descend_to_grasp.grasp_z_tolerance":0.015,"descend_to_place.place_speed":0.07848,"descend_to_place.place_z_tolerance":0.01733,"lift.lift_height":0.14856,"lift.lift_speed":0.03801},"optimized_scores":{"best_composite_score":-0.04735,"best_fitness_score":0.62265,"best_task_score":0.28326},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":671.0,"contact_point_centroid":[0.57606,0.10979,-0.00394],"force_p95":0.84957,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.4458,"mean_force":0.20156,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.59301,0.12056,0.25305]},{"body_a":"world","body_b":"grasp_target","contact_count":165.0,"contact_point_centroid":[0.47101,-0.01909,-0.0012],"force_p95":0.53221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60018,"mean_force":0.12849,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46275,-0.01942,0.02879]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6874.0,"contact_point_centroid":[0.48394,-0.01411,0.18363],"force_p95":0.1554,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28501,"mean_force":0.07672,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.48066,0.00459,0.18318]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21011.0,"contact_point_centroid":[0.45997,-0.03848,0.07568],"force_p95":0.07094,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26495,"mean_force":0.04855,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4602,-0.01934,0.07387]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20315.0,"contact_point_centroid":[0.46004,-0.00016,0.07584],"force_p95":0.07348,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26382,"mean_force":0.04971,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46021,-0.01934,0.0738]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6698.0,"contact_point_centroid":[0.48785,0.02697,0.18933],"force_p95":0.13559,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24934,"mean_force":0.07935,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.48423,0.00829,0.18866]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.01999,-0.00206],"force_p95":0.14043,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19314,"mean_force":0.12754,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46543,-0.01948,0.02841]},{"body_a":"world","body_b":"grasp_target","contact_count":384.0,"contact_point_centroid":[0.47616,-0.02015,-0.00168],"force_p95":0.13822,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12396,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.49188,-0.00587,0.27979]},{"body_a":"world","body_b":"grasp_target","contact_count":588.0,"contact_point_centroid":[0.57596,0.1097,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12266,"mean_force":0.12261,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61987,0.14997,0.21811]},{"body_a":"world","body_b":"grasp_target","contact_count":2668.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47625,-0.01627,0.1441]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4815.0,"contact_point_centroid":[0.46434,-0.00024,0.02968],"force_p95":0.06792,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09737,"mean_force":0.04488,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46431,-0.01945,0.02731]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5173.0,"contact_point_centroid":[0.46419,-0.03868,0.0292],"force_p95":0.06673,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08273,"mean_force":0.043,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46432,-0.01945,0.02732]},{"body_a":"left_finger","body_b":"right_finger","contact_count":527.0,"contact_point_centroid":[0.5992,0.12671,0.25369],"force_p95":0.01371,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01609,"mean_force":0.0111,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.59896,0.12671,0.25142]},{"body_a":"left_finger","body_b":"right_finger","contact_count":633.0,"contact_point_centroid":[0.62035,0.15001,0.22034],"force_p95":0.01107,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01108,"mean_force":0.01038,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61989,0.15,0.21794]}],"total_contact_groups":14},"final_pose_error":0.00981,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.57596,0.1097,0.01602],"final_tcp_position":[0.62437,0.15475,0.19518],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":2.4458,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":97.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02601],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28839,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12218,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":384.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.4827,-0.01297,0.25628],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23048,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":667.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02601],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28839,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2668.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.47215,-0.01962,0.03508],"tcp_start":[0.4827,-0.01297,0.25628],"tcp_to_object_dist_end":0.00993,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01948,0.02578],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28817,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13777,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11788.0,"raw_peak_contact_force":0.19314,"subtask_id":"grasp_object","tcp_end":[0.46428,-0.01945,0.02729],"tcp_start":[0.47215,-0.01962,0.03508],"tcp_to_object_dist_end":0.01185,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46914,-0.01928,0.11278],"object_pos_start":[0.47603,-0.01948,0.02578],"object_to_goal_dist_end":0.25329,"object_to_goal_dist_start":0.28817,"object_z_max":0.1127,"peak_contact_force":0.07059,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41491.0,"raw_peak_contact_force":0.60018,"subtask_id":"lift_object","tcp_end":[0.46028,-0.01934,0.12161],"tcp_start":[0.46428,-0.01945,0.02729],"tcp_to_object_dist_end":0.01251,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":808.0,"n_steps_budget":1000.0,"object_pos_end":[0.57596,0.1097,0.01601],"object_pos_start":[0.46914,-0.01928,0.11278],"object_to_goal_dist_end":0.18922,"object_to_goal_dist_start":0.25329,"object_z_max":0.22939,"peak_contact_force":0.12267,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14770.0,"raw_peak_contact_force":2.4458,"subtask_id":"approach_goal","tcp_end":[0.61708,0.14566,0.24201],"tcp_start":[0.46028,-0.01934,0.12161],"tcp_to_object_dist_end":0.23251,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":147.0,"n_steps_budget":1000.0,"object_pos_end":[0.57596,0.1097,0.01602],"object_pos_start":[0.57596,0.1097,0.01601],"object_to_goal_dist_end":0.18921,"object_to_goal_dist_start":0.18922,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1221.0,"raw_peak_contact_force":0.12266,"subtask_id":"place_object","tcp_end":[0.62437,0.15475,0.19518],"tcp_start":[0.61708,0.14566,0.24201],"tcp_to_object_dist_end":0.19097,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21753,"average_solve_count":308.0,"average_success_count":308.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.05044,"approach_above_goal.approach_goal_speed":0.02332,"approach_above_goal.arc_height":0.2406,"approach_above_object.approach_height":0.14942,"approach_above_object.approach_speed":0.16924,"descend_to_grasp.descent_speed":0.04884,"descend_to_grasp.grasp_z_tolerance":0.01359,"descend_to_place.place_speed":0.05332,"descend_to_place.place_z_tolerance":0.01216,"lift.lift_height":0.14573,"lift.lift_speed":0.03227},"optimized_scores":{"best_composite_score":0.3116,"best_fitness_score":0.9816,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":163.0,"contact_point_centroid":[0.45363,-0.02475,-0.00121],"force_p95":0.50406,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57493,"mean_force":0.1263,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44573,-0.02544,0.02951]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1942.0,"contact_point_centroid":[0.62255,0.21699,0.14473],"force_p95":0.14095,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35659,"mean_force":0.0941,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61843,0.19837,0.14664]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2044.0,"contact_point_centroid":[0.62198,0.17983,0.14531],"force_p95":0.13983,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34116,"mean_force":0.08696,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61832,0.19824,0.1474]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20795.0,"contact_point_centroid":[0.4432,-0.04443,0.08148],"force_p95":0.07166,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24279,"mean_force":0.04874,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44325,-0.02534,0.07942]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19214.0,"contact_point_centroid":[0.44341,-0.00616,0.07941],"force_p95":0.07473,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23035,"mean_force":0.05195,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44325,-0.02534,0.07702]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02616,-0.00207],"force_p95":0.14375,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20902,"mean_force":0.12843,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44831,-0.02554,0.02904]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.45856,-0.02632,-0.00184],"force_p95":0.1373,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12324,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.48238,-0.01009,0.25021]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17031.0,"contact_point_centroid":[0.51071,0.04082,0.20033],"force_p95":0.08774,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13706,"mean_force":0.05842,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.50876,0.05973,0.19957]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15849.0,"contact_point_centroid":[0.51574,0.08463,0.2021],"force_p95":0.08881,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13684,"mean_force":0.06215,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.5135,0.06563,0.20069]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5287.0,"contact_point_centroid":[0.44663,-0.00625,0.02961],"force_p95":0.06554,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12971,"mean_force":0.04114,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44723,-0.0255,0.02802]},{"body_a":"world","body_b":"grasp_target","contact_count":2264.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45805,-0.02342,0.11549]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5432.0,"contact_point_centroid":[0.44663,-0.04479,0.02946],"force_p95":0.06564,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08065,"mean_force":0.04118,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44723,-0.0255,0.02802]}],"total_contact_groups":12},"final_pose_error":0.00988,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.63168,0.20369,0.09852],"final_tcp_position":[0.62283,0.2036,0.11892],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.57493,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":201.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":800.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.46397,-0.02121,0.19765],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17179,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":566.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2264.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.45482,-0.02576,0.03524],"tcp_start":[0.46397,-0.02121,0.19765],"tcp_to_object_dist_end":0.00997,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02558,0.02574],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30322,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14104,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12519.0,"raw_peak_contact_force":0.20902,"subtask_id":"grasp_object","tcp_end":[0.4472,-0.02549,0.02799],"tcp_start":[0.45482,-0.02576,0.03524],"tcp_to_object_dist_end":0.01146,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45138,-0.02511,0.11927],"object_pos_start":[0.45844,-0.02558,0.02574],"object_to_goal_dist_end":0.29397,"object_to_goal_dist_start":0.30322,"object_z_max":0.11917,"peak_contact_force":0.07816,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40172.0,"raw_peak_contact_force":0.57493,"subtask_id":"lift_object","tcp_end":[0.4433,-0.02533,0.12835],"tcp_start":[0.4472,-0.02549,0.02799],"tcp_to_object_dist_end":0.01216,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62645,0.19422,0.158],"object_pos_start":[0.45138,-0.02511,0.11927],"object_to_goal_dist_end":0.0462,"object_to_goal_dist_start":0.29397,"object_z_max":0.21928,"peak_contact_force":0.09487,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32880.0,"raw_peak_contact_force":0.13706,"subtask_id":"approach_goal","tcp_end":[0.61656,0.19412,0.17579],"tcp_start":[0.4433,-0.02533,0.12835],"tcp_to_object_dist_end":0.02035,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":178.0,"n_steps_budget":1000.0,"object_pos_end":[0.63168,0.20369,0.09852],"object_pos_start":[0.62645,0.19422,0.158],"object_to_goal_dist_end":0.01631,"object_to_goal_dist_start":0.0462,"object_z_max":0.158,"peak_contact_force":0.14963,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3986.0,"raw_peak_contact_force":0.35659,"subtask_id":"place_object","tcp_end":[0.62283,0.2036,0.11892],"tcp_start":[0.61656,0.19412,0.17579],"tcp_to_object_dist_end":0.02223,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5665,"average_solve_count":203.0,"average_success_count":203.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.0756,"approach_above_goal.approach_goal_speed":0.11137,"approach_above_goal.arc_height":0.24939,"approach_above_object.approach_height":0.22005,"approach_above_object.approach_speed":0.14106,"descend_to_grasp.descent_speed":0.07551,"descend_to_grasp.grasp_z_tolerance":0.01264,"descend_to_place.place_speed":0.04386,"descend_to_place.place_z_tolerance":0.00776,"lift.lift_height":0.11957,"lift.lift_speed":0.06019},"optimized_scores":{"best_composite_score":-0.0591,"best_fitness_score":0.6109,"best_task_score":0.2681},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":929.0,"contact_point_centroid":[0.58169,0.09493,-0.0035],"force_p95":0.64538,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.08793,"mean_force":0.19328,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.60795,0.10921,0.26188]},{"body_a":"world","body_b":"grasp_target","contact_count":200.0,"contact_point_centroid":[0.53937,0.0007,-0.00114],"force_p95":0.48276,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72028,"mean_force":0.11345,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52774,0.00082,0.02549]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18564.0,"contact_point_centroid":[0.52625,-0.01831,0.07503],"force_p95":0.07831,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32051,"mean_force":0.05504,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5252,0.00078,0.0731]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18982.0,"contact_point_centroid":[0.52624,0.01985,0.07384],"force_p95":0.07773,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31118,"mean_force":0.05414,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52522,0.00078,0.07204]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5939.0,"contact_point_centroid":[0.53844,0.03615,0.17695],"force_p95":0.14689,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2931,"mean_force":0.07853,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.53531,0.01736,0.17746]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6348.0,"contact_point_centroid":[0.53771,-0.00206,0.17548],"force_p95":0.14649,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27698,"mean_force":0.07406,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.53468,0.01659,0.17632]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00098,-0.00203],"force_p95":0.13178,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16057,"mean_force":0.1253,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53099,0.00088,0.02536]},{"body_a":"world","body_b":"grasp_target","contact_count":432.0,"contact_point_centroid":[0.54431,0.00113,-0.00171],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12378,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.51301,0.00036,0.28153]},{"body_a":"world","body_b":"grasp_target","contact_count":760.0,"contact_point_centroid":[0.58078,0.09591,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12267,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63733,0.14838,0.22958]},{"body_a":"world","body_b":"grasp_target","contact_count":2816.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53195,0.00087,0.14542]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53079,-0.01834,0.02662],"force_p95":0.07605,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11026,"mean_force":0.0517,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52974,0.00086,0.02393]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53073,0.01994,0.02574],"force_p95":0.06806,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09676,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52974,0.00086,0.02393]},{"body_a":"left_finger","body_b":"right_finger","contact_count":854.0,"contact_point_centroid":[0.61209,0.11388,0.2652],"force_p95":0.01254,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01625,"mean_force":0.0107,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.61165,0.11387,0.26296]},{"body_a":"left_finger","body_b":"right_finger","contact_count":814.0,"contact_point_centroid":[0.63786,0.14841,0.23174],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01267,"mean_force":0.01041,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63734,0.14839,0.22951]}],"total_contact_groups":14},"final_pose_error":0.00976,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.58078,0.09591,0.01602],"final_tcp_position":[0.64153,0.15396,0.19752],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":2.08793,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":109.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12239,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":432.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52802,0.00074,0.26106],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23561,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":704.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2816.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.53845,0.00102,0.034],"tcp_start":[0.52802,0.00074,0.26106],"tcp_to_object_dist_end":0.0099,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54415,0.00072,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12966,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.16057,"subtask_id":"grasp_object","tcp_end":[0.52971,0.00086,0.02389],"tcp_start":[0.53845,0.00102,0.034],"tcp_to_object_dist_end":0.01458,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53687,0.00079,0.11241],"object_pos_start":[0.54415,0.00072,0.02588],"object_to_goal_dist_end":0.20785,"object_to_goal_dist_start":0.25053,"object_z_max":0.11231,"peak_contact_force":0.07896,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37746.0,"raw_peak_contact_force":0.72028,"subtask_id":"lift_object","tcp_end":[0.52535,0.00079,0.12158],"tcp_start":[0.52971,0.00086,0.02389],"tcp_to_object_dist_end":0.01473,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":805.0,"n_steps_budget":1000.0,"object_pos_end":[0.58078,0.09591,0.01602],"object_pos_start":[0.53687,0.00079,0.11241],"object_to_goal_dist_end":0.19746,"object_to_goal_dist_start":0.20785,"object_z_max":0.21471,"peak_contact_force":0.12267,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14070.0,"raw_peak_contact_force":2.08793,"subtask_id":"approach_goal","tcp_end":[0.63502,0.14352,0.26183],"tcp_start":[0.52535,0.00079,0.12158],"tcp_to_object_dist_end":0.25619,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":190.0,"n_steps_budget":1000.0,"object_pos_end":[0.58078,0.09591,0.01602],"object_pos_start":[0.58078,0.09591,0.01602],"object_to_goal_dist_end":0.19746,"object_to_goal_dist_start":0.19746,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1574.0,"raw_peak_contact_force":0.12267,"subtask_id":"place_object","tcp_end":[0.64153,0.15396,0.19752],"tcp_start":[0.63502,0.14352,0.26183],"tcp_to_object_dist_end":0.20001,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```