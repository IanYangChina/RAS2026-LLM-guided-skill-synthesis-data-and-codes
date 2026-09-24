## Search State

- **Seed**: 2
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | 0.0200 | 0.38 | ✅ accepted |
| 0 | align → align → pull → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | contact_detected | 0 | 0.1073 | 0.16 | ✅ accepted |

**Proposal policy**: task_score is 0.38 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.020) — your mutation base

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
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: approach_goal
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: place_object
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
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.15
    offset_along_axis:
      distance: 0.15
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
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift_object
- id: approach_above_goal
  type: approach
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_goal_speed:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: generator.speed
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
- id: release
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
    release_time:
      type: scalar
      range:
      - 0.3
      - 1.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace

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
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **approach_above_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_goal_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_time: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 0.020
- **task_score** (E): 0.380
- **fitness_score**: 0.670  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.650

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_object | 1.00 | 1.00 | 0.0758 |
| descend_to_grasp | 1.00 | 1.00 | 0.1986 |
| grasp | 1.00 | 1.00 | 0.0117 |
| lift | 0.00 | 1.00 | 0.0963 |
| approach_above_goal | 1.00 | 1.00 | 0.2981 |
| descend_to_place | 1.00 | 1.00 | 0.1258 |
| release | 1.00 | 1.00 | 0.0196 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, -0.010, 0.233) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.122 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.495, -0.010, 0.233)→(0.489, -0.015, 0.035) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.489, -0.015, 0.035)→(0.480, -0.015, 0.026) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 45.000 | 0.137 | 0.190 |
| lift | lift | 0.00 / step_budget | (0.480, -0.015, 0.026)→(0.481, -0.015, 0.123) | (0.493, -0.015, 0.026)→(0.490, -0.015, 0.113) | 0.281→0.250 | 1.00 / 41.333 | 0.073 | 0.654 |
| approach_above_goal | approach | 1.00 / step_budget | (0.481, -0.015, 0.123)→(0.629, 0.167, 0.299) | (0.490, -0.015, 0.113)→(0.606, 0.150, 0.086) | 0.250→0.160 | 1.00 / 16.667 | 3249.725 | 1.388 |
| descend_to_place | descend | 1.00 / step_budget | (0.629, 0.167, 0.299)→(0.632, 0.173, 0.173) | (0.606, 0.150, 0.086)→(0.604, 0.152, 0.042) | 0.160→0.130 | 1.00 / 17.333 | 0.122 | 0.167 |
| release | release | 1.00 / step_budget | (0.632, 0.173, 0.173)→(0.626, 0.171, 0.192) | (0.604, 0.152, 0.042)→(0.602, 0.150, 0.020) | 0.130→0.152 | 1.00 / 3.000 | 0.216 | 0.474 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.553
- phase_score: 0.559
- phase_breakdown.approach_object_score: 0.154
- phase_breakdown.grasp_object_score: 0.798
- phase_breakdown.lift_object_score: 0.348
- phase_breakdown.approach_goal_score: 0.673
- phase_breakdown.place_object_score: 0.822
- grasp_place_fitness: 0.758

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.758
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.553
- **Median Q (composite search score)**: -0.016
- **K-run variance**: 0.0039
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.337


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.49789,"average_solve_count":237.0,"average_success_count":237.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_speed":0.23275,"approach_above_object.approach_height":0.18164,"approach_above_object.approach_speed":0.14149,"descend_to_grasp.descent_speed":0.07717,"descend_to_grasp.grasp_z_tolerance":0.01131,"descend_to_place.place_speed":0.03152,"descend_to_place.place_z_tolerance":0.00841,"lift.lift_height":0.10967,"lift.lift_speed":0.045,"release.release_time":0.6716},"optimized_scores":{"best_composite_score":-0.01617,"best_fitness_score":0.63383,"best_task_score":0.30604},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":729.0,"contact_point_centroid":[0.60362,0.13724,-0.00376],"force_p95":0.78342,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.15662,"mean_force":0.19808,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.60773,0.13523,0.30306]},{"body_a":"world","body_b":"grasp_target","contact_count":167.0,"contact_point_centroid":[0.47142,-0.01915,-0.00119],"force_p95":0.50581,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62128,"mean_force":0.11562,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46273,-0.01948,0.02868]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8731.0,"contact_point_centroid":[0.51313,0.05088,0.17943],"force_p95":0.11811,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31568,"mean_force":0.0657,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.51031,0.03216,0.17864]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7525.0,"contact_point_centroid":[0.51044,0.01076,0.17683],"force_p95":0.13288,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28565,"mean_force":0.0742,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.50805,0.02969,0.17575]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20839.0,"contact_point_centroid":[0.46216,-0.03857,0.07486],"force_p95":0.07118,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27519,"mean_force":0.04896,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46234,-0.01942,0.07309]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20289.0,"contact_point_centroid":[0.46231,-0.00025,0.07573],"force_p95":0.07188,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27366,"mean_force":0.04986,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46238,-0.01942,0.07368]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02001,-0.00205],"force_p95":0.13896,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19088,"mean_force":0.12715,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46526,-0.01954,0.02818]},{"body_a":"world","body_b":"grasp_target","contact_count":560.0,"contact_point_centroid":[0.47616,-0.02015,-0.00177],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1235,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.4905,-0.00687,0.26677]},{"body_a":"world","body_b":"grasp_target","contact_count":1388.0,"contact_point_centroid":[0.60355,0.13701,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12268,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62461,0.15431,0.26177]},{"body_a":"world","body_b":"grasp_target","contact_count":2500.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47496,-0.0172,0.13117]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.60355,0.13701,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62299,0.1561,0.198]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5060.0,"contact_point_centroid":[0.46382,-0.0003,0.02962],"force_p95":0.066,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09552,"mean_force":0.04286,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46414,-0.01952,0.02708]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5167.0,"contact_point_centroid":[0.46406,-0.03877,0.02905],"force_p95":0.06674,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0818,"mean_force":0.04304,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46415,-0.01952,0.02709]},{"body_a":"left_finger","body_b":"right_finger","contact_count":614.0,"contact_point_centroid":[0.61154,0.1388,0.30957],"force_p95":0.01368,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01638,"mean_force":0.01097,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.61114,0.1388,0.30737]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1489.0,"contact_point_centroid":[0.62515,0.15432,0.26414],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01261,"mean_force":0.01039,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62461,0.15431,0.26182]},{"body_a":"left_finger","body_b":"right_finger","contact_count":218.0,"contact_point_centroid":[0.62575,0.15686,0.19664],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.01022,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62541,0.15684,0.19449]}],"total_contact_groups":16},"final_pose_error":0.0097,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.60355,0.13701,0.01602],"final_tcp_position":[0.62707,0.15727,0.19847],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":9748.96533,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":141.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":560.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48032,-0.01478,0.23022],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20431,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":625.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2500.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.47199,-0.01968,0.03485],"tcp_start":[0.48032,-0.01478,0.23022],"tcp_to_object_dist_end":0.00978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01957,0.0258],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28822,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13663,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12027.0,"raw_peak_contact_force":0.19088,"subtask_id":"grasp_object","tcp_end":[0.46412,-0.01951,0.02706],"tcp_start":[0.47199,-0.01968,0.03485],"tcp_to_object_dist_end":0.01198,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47344,-0.01937,0.11085],"object_pos_start":[0.47603,-0.01957,0.0258],"object_to_goal_dist_end":0.25122,"object_to_goal_dist_start":0.28822,"object_z_max":0.11076,"peak_contact_force":0.07196,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41295.0,"raw_peak_contact_force":0.62128,"subtask_id":"lift_object","tcp_end":[0.46453,-0.01942,0.11982],"tcp_start":[0.46412,-0.01951,0.02706],"tcp_to_object_dist_end":0.01263,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":869.0,"n_steps_budget":1000.0,"object_pos_end":[0.60355,0.137,0.01602],"object_pos_start":[0.47344,-0.01937,0.11085],"object_to_goal_dist_end":0.17761,"object_to_goal_dist_start":0.25122,"object_z_max":0.23316,"peak_contact_force":9748.96533,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17599.0,"raw_peak_contact_force":2.15662,"subtask_id":"approach_goal","tcp_end":[0.62364,0.15201,0.32321],"tcp_start":[0.46453,-0.01942,0.11982],"tcp_to_object_dist_end":0.30821,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":347.0,"n_steps_budget":1000.0,"object_pos_end":[0.60355,0.13701,0.01602],"object_pos_start":[0.60355,0.137,0.01602],"object_to_goal_dist_end":0.17761,"object_to_goal_dist_start":0.17761,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2877.0,"raw_peak_contact_force":0.12268,"subtask_id":"place_object","tcp_end":[0.62707,0.15727,0.19847],"tcp_start":[0.62364,0.15201,0.32321],"tcp_to_object_dist_end":0.18507,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60355,0.13701,0.01602],"object_pos_start":[0.60355,0.13701,0.01602],"object_to_goal_dist_end":0.17761,"object_to_goal_dist_start":0.17761,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62158,0.15564,0.21738],"tcp_start":[0.62707,0.15727,0.19847],"tcp_to_object_dist_end":0.20302,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77957,"average_solve_count":186.0,"average_success_count":186.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_speed":0.2147,"approach_above_object.approach_height":0.23133,"approach_above_object.approach_speed":0.16348,"descend_to_grasp.descent_speed":0.09546,"descend_to_grasp.grasp_z_tolerance":0.00802,"descend_to_place.place_speed":0.08752,"descend_to_place.place_z_tolerance":0.01152,"lift.lift_height":0.13501,"lift.lift_speed":0.04403,"release.release_time":0.536},"optimized_scores":{"best_composite_score":0.10834,"best_fitness_score":0.75834,"best_task_score":0.55258},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":185.0,"contact_point_centroid":[0.60268,0.19276,-0.00607],"force_p95":1.08167,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.17721,"mean_force":0.36921,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61781,0.203,0.12602]},{"body_a":"world","body_b":"grasp_target","contact_count":160.0,"contact_point_centroid":[0.4549,-0.02458,-0.0012],"force_p95":0.47463,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63821,"mean_force":0.09501,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44611,-0.02531,0.02971]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20806.0,"contact_point_centroid":[0.44548,-0.04438,0.07974],"force_p95":0.07114,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28381,"mean_force":0.04891,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44563,-0.02522,0.07793]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1214.0,"contact_point_centroid":[0.62085,0.18521,0.11711],"force_p95":0.12305,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28343,"mean_force":0.07135,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62209,0.20459,0.11673]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20732.0,"contact_point_centroid":[0.44549,-0.00605,0.08043],"force_p95":0.07102,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27581,"mean_force":0.04866,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44566,-0.02522,0.07846]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1132.0,"contact_point_centroid":[0.62132,0.22319,0.11707],"force_p95":0.09359,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26289,"mean_force":0.04769,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62238,0.2047,0.11723]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4891.0,"contact_point_centroid":[0.62332,0.1823,0.1847],"force_p95":0.12661,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25469,"mean_force":0.08006,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6216,0.20143,0.1848]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02616,-0.00208],"force_p95":0.14706,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21852,"mean_force":0.12917,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44862,-0.0254,0.02908]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6203.0,"contact_point_centroid":[0.62251,0.22001,0.18361],"force_p95":0.10336,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21806,"mean_force":0.06015,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62163,0.20148,0.18361]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13585.0,"contact_point_centroid":[0.53121,0.06385,0.18736],"force_p95":0.09305,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19291,"mean_force":0.06274,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.52991,0.08299,0.18584]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16268.0,"contact_point_centroid":[0.53199,0.10336,0.18766],"force_p95":0.08228,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16451,"mean_force":0.05288,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.53101,0.08446,0.18661]},{"body_a":"world","body_b":"grasp_target","contact_count":352.0,"contact_point_centroid":[0.45856,-0.02632,-0.00165],"force_p95":0.13823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12413,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.48699,-0.00746,0.28691]},{"body_a":"world","body_b":"grasp_target","contact_count":2968.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46261,-0.02104,0.15196]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5279.0,"contact_point_centroid":[0.44688,-0.00615,0.02935],"force_p95":0.06655,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10553,"mean_force":0.04105,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44754,-0.02536,0.02806]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5242.0,"contact_point_centroid":[0.44723,-0.04466,0.02954],"force_p95":0.06742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08501,"mean_force":0.04269,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44754,-0.02536,0.02807]}],"total_contact_groups":15},"final_pose_error":0.00979,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61295,0.19971,0.02723],"final_tcp_position":[0.62468,0.20545,0.12176],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.17721,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":89.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02599],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30366,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12209,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":352.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.4723,-0.01652,0.27191],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.24649,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":742.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02599],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30366,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2968.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.45514,-0.02562,0.03531],"tcp_start":[0.4723,-0.01652,0.27191],"tcp_to_object_dist_end":0.00992,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02544,0.0257],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30313,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14414,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12321.0,"raw_peak_contact_force":0.21852,"subtask_id":"grasp_object","tcp_end":[0.44751,-0.02536,0.02804],"tcp_start":[0.45514,-0.02562,0.03531],"tcp_to_object_dist_end":0.01118,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45618,-0.02524,0.11877],"object_pos_start":[0.45844,-0.02544,0.0257],"object_to_goal_dist_end":0.29118,"object_to_goal_dist_start":0.30313,"object_z_max":0.11868,"peak_contact_force":0.07203,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41698.0,"raw_peak_contact_force":0.63821,"subtask_id":"lift_object","tcp_end":[0.44766,-0.02523,0.12842],"tcp_start":[0.44751,-0.02536,0.02804],"tcp_to_object_dist_end":0.01287,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":838.0,"n_steps_budget":1000.0,"object_pos_end":[0.62624,0.19854,0.22473],"object_pos_start":[0.45618,-0.02524,0.11877],"object_to_goal_dist_end":0.1111,"object_to_goal_dist_start":0.29118,"object_z_max":0.22465,"peak_contact_force":0.0883,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29853.0,"raw_peak_contact_force":0.19291,"subtask_id":"approach_goal","tcp_end":[0.62048,0.19815,0.25003],"tcp_start":[0.44766,-0.02523,0.12842],"tcp_to_object_dist_end":0.02595,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":339.0,"n_steps_budget":1000.0,"object_pos_end":[0.62077,0.20508,0.09406],"object_pos_start":[0.62624,0.19854,0.22473],"object_to_goal_dist_end":0.02236,"object_to_goal_dist_start":0.1111,"object_z_max":0.22473,"peak_contact_force":0.12015,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11094.0,"raw_peak_contact_force":0.25469,"subtask_id":"place_object","tcp_end":[0.62468,0.20545,0.12176],"tcp_start":[0.62048,0.19815,0.25003],"tcp_to_object_dist_end":0.02798,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61295,0.19971,0.02723],"object_pos_start":[0.62077,0.20508,0.09406],"object_to_goal_dist_end":0.08897,"object_to_goal_dist_start":0.02236,"object_z_max":0.09406,"peak_contact_force":0.40217,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2531.0,"raw_peak_contact_force":1.17721,"tcp_end":[0.61767,0.20294,0.1403],"tcp_start":[0.62468,0.20545,0.12176],"tcp_to_object_dist_end":0.11321,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58378,"average_solve_count":185.0,"average_success_count":185.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_speed":0.14902,"approach_above_object.approach_height":0.15029,"approach_above_object.approach_speed":0.12854,"descend_to_grasp.descent_speed":0.10261,"descend_to_grasp.grasp_z_tolerance":0.01284,"descend_to_place.place_speed":0.05472,"descend_to_place.place_z_tolerance":0.01045,"lift.lift_height":0.16822,"lift.lift_speed":0.05916,"release.release_time":0.51329},"optimized_scores":{"best_composite_score":-0.03206,"best_fitness_score":0.61794,"best_task_score":0.28197},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1512.0,"contact_point_centroid":[0.58932,0.11366,-0.00269],"force_p95":0.34682,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.81322,"mean_force":0.15869,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.61817,0.12097,0.28153]},{"body_a":"world","body_b":"grasp_target","contact_count":210.0,"contact_point_centroid":[0.53982,0.0007,-0.00113],"force_p95":0.46491,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70206,"mean_force":0.10408,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52794,0.00082,0.02545]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6038.0,"contact_point_centroid":[0.55562,0.05326,0.1614],"force_p95":0.15202,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31489,"mean_force":0.07545,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.55239,0.0347,0.16207]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18606.0,"contact_point_centroid":[0.52871,-0.01833,0.07406],"force_p95":0.07823,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31177,"mean_force":0.05485,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52768,0.00076,0.07213]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19022.0,"contact_point_centroid":[0.52866,0.01983,0.07289],"force_p95":0.0777,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30302,"mean_force":0.05396,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52765,0.00076,0.0711]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5232.0,"contact_point_centroid":[0.55406,0.0143,0.15967],"force_p95":0.1638,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28309,"mean_force":0.08057,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.55121,0.03308,0.1599]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00098,-0.00203],"force_p95":0.13176,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16048,"mean_force":0.1253,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53108,0.00088,0.02529]},{"body_a":"world","body_b":"grasp_target","contact_count":844.0,"contact_point_centroid":[0.54431,0.00113,-0.00185],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12321,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.51551,0.00042,0.24935]},{"body_a":"world","body_b":"grasp_target","contact_count":1972.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.5345,0.00093,0.11388]},{"body_a":"world","body_b":"grasp_target","contact_count":1320.0,"contact_point_centroid":[0.58902,0.11368,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64191,0.15348,0.26248]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58902,0.11368,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63943,0.15506,0.19873]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53085,-0.01834,0.02655],"force_p95":0.07605,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11019,"mean_force":0.0517,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52982,0.00086,0.02386]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53079,0.01994,0.02567],"force_p95":0.06805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09673,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52983,0.00086,0.02386]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1432.0,"contact_point_centroid":[0.62115,0.12423,0.28825],"force_p95":0.01192,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01628,"mean_force":0.01068,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.62067,0.12422,0.28605]},{"body_a":"left_finger","body_b":"right_finger","contact_count":216.0,"contact_point_centroid":[0.64238,0.15582,0.19778],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01282,"mean_force":0.01028,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.64186,0.1558,0.19558]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1406.0,"contact_point_centroid":[0.64234,0.15349,0.26472],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01046,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64191,0.15348,0.26251]}],"total_contact_groups":16},"final_pose_error":0.00973,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.58902,0.11368,0.01602],"final_tcp_position":[0.6435,0.15621,0.19971],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.81322,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":212.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":844.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53318,0.00088,0.19672],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17107,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":493.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1972.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.53853,0.00102,0.03393],"tcp_start":[0.53318,0.00088,0.19672],"tcp_to_object_dist_end":0.00979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54415,0.00073,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12965,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.16048,"subtask_id":"grasp_object","tcp_end":[0.52979,0.00086,0.02383],"tcp_start":[0.53853,0.00102,0.03393],"tcp_to_object_dist_end":0.0145,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54148,0.00075,0.11054],"object_pos_start":[0.54415,0.00073,0.02588],"object_to_goal_dist_end":0.20618,"object_to_goal_dist_start":0.25053,"object_z_max":0.11044,"peak_contact_force":0.07413,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37838.0,"raw_peak_contact_force":0.70206,"subtask_id":"lift_object","tcp_end":[0.52996,0.00075,0.11965],"tcp_start":[0.52979,0.00086,0.02383],"tcp_to_object_dist_end":0.01468,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":911.0,"n_steps_budget":1000.0,"object_pos_end":[0.58902,0.11368,0.01602],"object_pos_start":[0.54148,0.00075,0.11054],"object_to_goal_dist_end":0.1899,"object_to_goal_dist_start":0.20618,"object_z_max":0.19301,"peak_contact_force":0.12263,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14214.0,"raw_peak_contact_force":1.81322,"subtask_id":"approach_goal","tcp_end":[0.6415,0.15133,0.32347],"tcp_start":[0.52996,0.00075,0.11965],"tcp_to_object_dist_end":0.31416,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":330.0,"n_steps_budget":1000.0,"object_pos_end":[0.58902,0.11368,0.01602],"object_pos_start":[0.58902,0.11368,0.01602],"object_to_goal_dist_end":0.1899,"object_to_goal_dist_start":0.1899,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2726.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.6435,0.15621,0.19971],"tcp_start":[0.6415,0.15133,0.32347],"tcp_to_object_dist_end":0.19626,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58902,0.11368,0.01602],"object_pos_start":[0.58902,0.11368,0.01602],"object_to_goal_dist_end":0.1899,"object_to_goal_dist_start":0.1899,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1016.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63802,0.15461,0.21788],"tcp_start":[0.6435,0.15621,0.19971],"tcp_to_object_dist_end":0.21172,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```