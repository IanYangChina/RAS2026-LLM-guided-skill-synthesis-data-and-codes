## Search State

- **Seed**: 8
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | descend → grasp → lift → approach → descend → release | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.2065 | 0.29 | ✅ accepted |
| 6 | descend → grasp → lift → descend → descend → release | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2419 | 0.29 | ❌ rejected |
| 5 | descend → grasp → lift → approach → descend → release | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2314 | 0.24 | ❌ rejected |
| 4 | descend → grasp → lift → approach → descend → release | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1488 | 0.19 | ❌ rejected |
| 3 | descend → grasp → lift → approach → descend → release | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1969 | 0.28 | ❌ rejected |

**Proposal policy**: task_score is 0.29 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`
- Frozen object start: [0.48269722766055606, 0.048727684333792556, 0.03]
- Frozen task target: [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]
- Goal object position: (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.48269722766055606, 0.048727684333792556, 0.03)
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
  frozen_object_start: [0.4827, 0.0487, 0.03]
  frozen_task_target: [0.5819, 0.2289, 0.2305]
  frozen_object_starts: {'grasp_target': [0.48269722766055606, 0.048727684333792556, 0.03]}
  frozen_targets: {'place_target': [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c

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
| `object` | offset from object initial position (0.48269722766055606, 0.048727684333792556, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5818710838485517, 0.2288548935820029, 0.2304844767544324) | final destination targets |
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
skill_type: arm_gripper
subtasks:
- id: pre_grasp
  anchor: object
  weight: 0.2
- id: lift_clear
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.3
- id: place
  weight: 0.5
phases:
- id: descend_1
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
    descend_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: pre_grasp
- id: grasp_1
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
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
- id: lift_1
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
    - 0.12
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: lift_clear
- id: transport_1
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: grasp_retained
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
- id: descend_2
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
    - 0.01
    tolerance: 0.008
    orientation:
      mode: keep_current
  parameters:
    place_z_offset:
      type: scalar
      range:
      - -0.01
      - 0.03
      default: 0.01
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place
- id: release_1
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
    release_duration:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: duration.max_time
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=bilateral_check, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=grasp_retained, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=1, strategy=reduce_speed
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.01], tolerance=0.008
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 0.206
- **task_score** (E): 0.295
- **fitness_score**: 0.626  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.420

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_1 | 1.00 | 1.00 | 0.2665 |
| grasp_1 | 0.00 | 1.00 | 0.0000 |
| lift_1 | 1.00 | 1.00 | 0.1014 |
| transport_1 | 0.33 | 1.00 | 0.2726 |
| descend_2 | 1.00 | 1.00 | 0.1085 |
| release_1 | 1.00 | 1.00 | 0.0202 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_1 | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.038) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| grasp_1 | grasp | 0.00 / guard_failure | (0.511, -0.001, 0.032)→(0.511, -0.001, 0.032) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.025) | 0.289→0.290 | 1.00 / 45.333 | 0.166 | 0.249 |
| lift_1 | lift | 1.00 / step_budget | (0.511, -0.001, 0.032)→(0.507, -0.001, 0.134) | (0.522, -0.001, 0.025)→(0.522, -0.001, 0.120) | 0.290→0.242 | 1.00 / 25.000 | 82.875 | 0.627 |
| transport_1 | approach | 0.33 / step_budget | (0.507, -0.001, 0.134)→(0.592, 0.176, 0.321) | (0.522, -0.001, 0.120)→(0.598, 0.176, 0.295) | 0.242→0.098 | 1.00 / 15.333 | 0.154 | 0.175 |
| descend_2 | descend | 1.00 / step_budget | (0.592, 0.176, 0.321)→(0.603, 0.203, 0.217) | (0.598, 0.176, 0.295)→(0.602, 0.205, 0.119) | 0.098→0.087 | 1.00 / 17.000 | 0.145 | 0.994 |
| release_1 | release | 1.00 / step_budget | (0.603, 0.203, 0.217)→(0.599, 0.201, 0.237) | (0.602, 0.205, 0.119)→(0.599, 0.203, 0.020) | 0.087→0.185 | 1.00 / 3.667 | 0.167 | 1.081 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.356
- phase_score: 0.721
- phase_breakdown.pre_grasp_score: 0.768
- phase_breakdown.lift_clear_score: 0.607
- phase_breakdown.place_score: 0.771
- grasp_place_fitness: 0.654

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.654
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.356
- **Median Q (composite search score)**: 0.200
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.199


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2cbd02033d1f1347f2ac2d0b012406a96501e6b48f5b172bd88b34d6c745630c`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5745d7c2d025a63f908a4bf0f58182445bb06541d436718f39304ac5569d60c0`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4619,"average_solve_count":210.0,"average_success_count":210.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":-0.00684,"descend_2.place_z_offset":0.01116,"lift_1.lift_height":0.12211,"release_1.release_duration":0.24744,"transport_1.approach_height":0.16256,"transport_1.transport_speed":0.05925},"optimized_scores":{"best_composite_score":0.18573,"best_fitness_score":0.60573,"best_task_score":0.23897},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":749.0,"contact_point_centroid":[0.57302,0.23416,-0.00403],"force_p95":0.90104,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.39433,"mean_force":0.21065,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.5728,0.21719,0.27293]},{"body_a":"world","body_b":"grasp_target","contact_count":149.0,"contact_point_centroid":[0.47936,0.04369,-0.00142],"force_p95":0.50989,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73381,"mean_force":0.0929,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47278,0.04534,0.0291]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12610.0,"contact_point_centroid":[0.47121,0.06425,0.07955],"force_p95":0.08629,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33834,"mean_force":0.05684,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47039,0.04512,0.07753]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13147.0,"contact_point_centroid":[0.47125,0.0261,0.08182],"force_p95":0.08456,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30197,"mean_force":0.05378,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47039,0.04512,0.07996]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.48282,0.04808,-0.00238],"force_p95":0.2091,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28928,"mean_force":0.14994,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47481,0.04556,0.02733]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":253.0,"contact_point_centroid":[0.56893,0.18328,0.33683],"force_p95":0.20676,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24706,"mean_force":0.14872,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.56382,0.20134,0.34163]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":443.0,"contact_point_centroid":[0.56825,0.21886,0.33503],"force_p95":0.16084,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23683,"mean_force":0.09461,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.56391,0.20159,0.33997]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12154.0,"contact_point_centroid":[0.51603,0.0993,0.23277],"force_p95":0.12784,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17488,"mean_force":0.08011,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51227,0.11778,0.23353]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11993.0,"contact_point_centroid":[0.51766,0.13825,0.23586],"force_p95":0.12762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17235,"mean_force":0.08136,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51347,0.11973,0.2362]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5691.0,"contact_point_centroid":[0.47455,0.02632,0.02884],"force_p95":0.08051,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16212,"mean_force":0.04535,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47438,0.04551,0.02689]},{"body_a":"world","body_b":"grasp_target","contact_count":3336.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48846,0.02291,0.16425]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57294,0.23398,-0.00199],"force_p95":0.12265,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12275,"mean_force":0.12262,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57391,0.22295,0.24651]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6192.0,"contact_point_centroid":[0.47452,0.06494,0.0288],"force_p95":0.08148,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08706,"mean_force":0.04516,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47439,0.04551,0.0269]},{"body_a":"left_finger","body_b":"right_finger","contact_count":670.0,"contact_point_centroid":[0.57407,0.21841,0.27077],"force_p95":0.01245,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01574,"mean_force":0.01073,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57352,0.21838,0.26839]},{"body_a":"left_finger","body_b":"right_finger","contact_count":226.0,"contact_point_centroid":[0.57629,0.22391,0.24462],"force_p95":0.0109,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01093,"mean_force":0.00989,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57578,0.22388,0.24249]}],"total_contact_groups":15},"final_pose_error":0.00791,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.57294,0.23398,0.01602],"final_tcp_position":[0.57707,0.22429,0.24598],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":2.39433,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":835.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3336.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.47915,0.04593,0.03185],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.00738,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48261,0.04581,0.02489],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29262,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.19157,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13687.0,"raw_peak_contact_force":0.28928,"tcp_end":[0.47436,0.0455,0.02687],"tcp_start":[0.47436,0.0455,0.02687],"tcp_to_object_dist_end":0.00849,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.48613,0.04557,0.12848],"object_pos_start":[0.48261,0.04579,0.02494],"object_to_goal_dist_end":0.23057,"object_to_goal_dist_start":0.2926,"object_z_max":0.12837,"peak_contact_force":0.10518,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25906.0,"raw_peak_contact_force":0.73381,"subtask_id":"lift_clear","tcp_end":[0.4705,0.04514,0.13752],"tcp_start":[0.47436,0.0455,0.02687],"tcp_to_object_dist_end":0.01806,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56979,0.20033,0.32286],"object_pos_start":[0.48613,0.04557,0.12848],"object_to_goal_dist_end":0.09744,"object_to_goal_dist_start":0.23057,"object_z_max":0.32266,"peak_contact_force":0.15762,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24147.0,"raw_peak_contact_force":0.17488,"tcp_end":[0.56349,0.2003,0.34661],"tcp_start":[0.4705,0.04514,0.13752],"tcp_to_object_dist_end":0.02456,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":343.0,"n_steps_budget":1000.0,"object_pos_end":[0.57294,0.23397,0.01602],"object_pos_start":[0.56979,0.20033,0.32286],"object_to_goal_dist_end":0.21471,"object_to_goal_dist_start":0.09744,"object_z_max":0.32296,"peak_contact_force":0.12276,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2115.0,"raw_peak_contact_force":2.39433,"subtask_id":"place","tcp_end":[0.57707,0.22429,0.24598],"tcp_start":[0.56349,0.2003,0.34661],"tcp_to_object_dist_end":0.2302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57294,0.23398,0.01602],"object_pos_start":[0.57294,0.23397,0.01602],"object_to_goal_dist_end":0.21471,"object_to_goal_dist_start":0.21471,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12275,"tcp_end":[0.57287,0.22241,0.26623],"tcp_start":[0.57707,0.22429,0.24598],"tcp_to_object_dist_end":0.25048,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2b35d39beba75b46a5edd8e67b975c00ef2c88fb75a3753bdd32db5918adf9e2`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43842,"average_solve_count":203.0,"average_success_count":203.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":0.00452,"descend_2.place_z_offset":0.00957,"lift_1.lift_height":0.10946,"release_1.release_duration":0.28698,"transport_1.approach_height":0.15184,"transport_1.transport_speed":0.04767},"optimized_scores":{"best_composite_score":0.20015,"best_fitness_score":0.62015,"best_task_score":0.28907},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":180.0,"contact_point_centroid":[0.59295,0.21432,-0.00749],"force_p95":1.24653,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.77128,"mean_force":0.40187,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60044,0.21973,0.2294]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.53394,-0.01938,-0.00121],"force_p95":0.41753,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56106,"mean_force":0.08243,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52368,-0.02008,0.03747]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":675.0,"contact_point_centroid":[0.60809,0.20287,0.21128],"force_p95":0.1344,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41472,"mean_force":0.08062,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60356,0.2212,0.21348]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":630.0,"contact_point_centroid":[0.60818,0.23937,0.21081],"force_p95":0.13065,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40231,"mean_force":0.0798,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60359,0.22122,0.21352]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10740.0,"contact_point_centroid":[0.52265,-0.03897,0.07987],"force_p95":0.09885,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30319,"mean_force":0.05879,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5211,-0.02002,0.07831]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10166.0,"contact_point_centroid":[0.52267,-0.00103,0.0819],"force_p95":0.09875,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30089,"mean_force":0.06102,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5211,-0.02002,0.07989]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3532.0,"contact_point_centroid":[0.60342,0.22122,0.25432],"force_p95":0.15664,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29689,"mean_force":0.0983,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59868,0.20334,0.25621]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4119.0,"contact_point_centroid":[0.60258,0.18383,0.25742],"force_p95":0.15555,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24529,"mean_force":0.09691,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59814,0.2018,0.25959]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53707,-0.02111,-0.00213],"force_p95":0.15375,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22256,"mean_force":0.13246,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5258,-0.02012,0.03625]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12061.0,"contact_point_centroid":[0.5571,0.09373,0.21382],"force_p95":0.12637,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17579,"mean_force":0.07821,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5526,0.07517,0.21352]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12659.0,"contact_point_centroid":[0.5574,0.05755,0.2146],"force_p95":0.11255,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15686,"mean_force":0.07543,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55293,0.07604,0.21431]},{"body_a":"world","body_b":"grasp_target","contact_count":3312.0,"contact_point_centroid":[0.53702,-0.02132,-0.00195],"force_p95":0.12693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51411,-0.01006,0.16928]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5807.0,"contact_point_centroid":[0.52529,-0.0009,0.03799],"force_p95":0.06996,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11078,"mean_force":0.04513,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52533,-0.02011,0.0357]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6271.0,"contact_point_centroid":[0.52514,-0.03934,0.03753],"force_p95":0.06887,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07336,"mean_force":0.04312,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52534,-0.02011,0.03571]}],"total_contact_groups":14},"final_pose_error":0.00797,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.60069,0.21692,0.02181],"final_tcp_position":[0.60524,0.22165,0.21767],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":248.41632,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":829.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3312.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53043,-0.02018,0.04171],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01706,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53695,-0.02034,0.0256],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3162,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14803,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13882.0,"raw_peak_contact_force":0.22256,"tcp_end":[0.52531,-0.02011,0.03567],"tcp_start":[0.52531,-0.02011,0.03568],"tcp_to_object_dist_end":0.01539,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":604.0,"n_steps_budget":690.0,"object_pos_end":[0.53558,-0.02011,0.116],"object_pos_start":[0.53695,-0.02032,0.02563],"object_to_goal_dist_end":0.27455,"object_to_goal_dist_start":0.31617,"object_z_max":0.11589,"peak_contact_force":248.41632,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21052.0,"raw_peak_contact_force":0.56106,"subtask_id":"lift_clear","tcp_end":[0.52117,-0.02001,0.13258],"tcp_start":[0.52531,-0.02011,0.03567],"tcp_to_object_dist_end":0.02196,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59698,0.18164,0.28269],"object_pos_start":[0.53558,-0.02011,0.116],"object_to_goal_dist_end":0.08928,"object_to_goal_dist_start":0.27455,"object_z_max":0.28252,"peak_contact_force":0.15263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24720.0,"raw_peak_contact_force":0.17579,"tcp_end":[0.59196,0.1814,0.30931],"tcp_start":[0.52117,-0.02001,0.13258],"tcp_to_object_dist_end":0.02709,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":365.0,"n_steps_budget":1000.0,"object_pos_end":[0.60553,0.22079,0.18562],"object_pos_start":[0.59698,0.18164,0.28269],"object_to_goal_dist_end":0.02337,"object_to_goal_dist_start":0.08928,"object_z_max":0.28274,"peak_contact_force":0.1485,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7651.0,"raw_peak_contact_force":0.29689,"subtask_id":"place","tcp_end":[0.60524,0.22165,0.21767],"tcp_start":[0.59196,0.1814,0.30931],"tcp_to_object_dist_end":0.03206,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60069,0.21692,0.02181],"object_pos_start":[0.60553,0.22079,0.18562],"object_to_goal_dist_end":0.18616,"object_to_goal_dist_start":0.02337,"object_z_max":0.18562,"peak_contact_force":0.22651,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1485.0,"raw_peak_contact_force":1.77128,"tcp_end":[0.60042,0.21972,0.23695],"tcp_start":[0.60524,0.22165,0.21767],"tcp_to_object_dist_end":0.21515,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `530652a2467d9ac78fab654e7ed7fc5283ca1649270bc8f158e04c16074f9f95`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43182,"average_solve_count":220.0,"average_success_count":220.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":0.00418,"descend_2.place_z_offset":0.00635,"lift_1.lift_height":0.10924,"release_1.release_duration":0.2486,"transport_1.approach_height":0.15852,"transport_1.transport_speed":0.04217},"optimized_scores":{"best_composite_score":0.23355,"best_fitness_score":0.65355,"best_task_score":0.35587},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":190.0,"contact_point_centroid":[0.6151,0.15817,-0.00657],"force_p95":1.23739,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.34778,"mean_force":0.35597,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6224,0.16012,0.2002]},{"body_a":"world","body_b":"grasp_target","contact_count":148.0,"contact_point_centroid":[0.54262,-0.02683,-0.00126],"force_p95":0.41641,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58711,"mean_force":0.08598,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53165,-0.02748,0.03666]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":776.0,"contact_point_centroid":[0.628,0.1428,0.17957],"force_p95":0.25551,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37716,"mean_force":0.10096,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62581,0.16122,0.18354]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":678.0,"contact_point_centroid":[0.62815,0.17939,0.17922],"force_p95":0.28902,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37488,"mean_force":0.10433,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62583,0.16122,0.18358]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10757.0,"contact_point_centroid":[0.53084,-0.04628,0.07885],"force_p95":0.09829,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31545,"mean_force":0.05865,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52906,-0.02739,0.07743]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9750.0,"contact_point_centroid":[0.53079,-0.00836,0.08024],"force_p95":0.10394,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30688,"mean_force":0.06327,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52907,-0.02739,0.07816]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3326.0,"contact_point_centroid":[0.62843,0.17218,0.2389],"force_p95":0.15904,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29225,"mean_force":0.10357,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62421,0.15438,0.24132]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3778.0,"contact_point_centroid":[0.62808,0.136,0.24171],"force_p95":0.16499,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25419,"mean_force":0.10561,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62402,0.15399,0.24431]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.54568,-0.02895,-0.00219],"force_p95":0.16563,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23488,"mean_force":0.13607,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53383,-0.02756,0.03542]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11433.0,"contact_point_centroid":[0.5737,0.07079,0.20941],"force_p95":0.14694,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17494,"mean_force":0.08129,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56922,0.05226,0.20941]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12280.0,"contact_point_centroid":[0.57458,0.03554,0.21106],"force_p95":0.11988,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15942,"mean_force":0.07681,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57018,0.05396,0.21121]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6083.0,"contact_point_centroid":[0.53306,-0.00829,0.03771],"force_p95":0.06945,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15187,"mean_force":0.04315,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53335,-0.02754,0.03486]},{"body_a":"world","body_b":"grasp_target","contact_count":3388.0,"contact_point_centroid":[0.5456,-0.02923,-0.00195],"force_p95":0.12666,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51819,-0.01382,0.16871]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6623.0,"contact_point_centroid":[0.53292,-0.04684,0.03717],"force_p95":0.06968,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0754,"mean_force":0.04129,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53336,-0.02754,0.03486]}],"total_contact_groups":14},"final_pose_error":0.00783,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.62208,0.15864,0.02244],"final_tcp_position":[0.62806,0.16177,0.18859],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.34778,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":848.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3388.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53851,-0.02767,0.04105],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01669,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54554,-0.02787,0.02546],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26026,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.15772,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":14510.0,"raw_peak_contact_force":0.23488,"tcp_end":[0.53333,-0.02753,0.03483],"tcp_start":[0.53333,-0.02753,0.03483],"tcp_to_object_dist_end":0.0154,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.54374,-0.02748,0.1152],"object_pos_start":[0.54555,-0.02784,0.02549],"object_to_goal_dist_end":0.22084,"object_to_goal_dist_start":0.26022,"object_z_max":0.11509,"peak_contact_force":0.10454,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20655.0,"raw_peak_contact_force":0.58711,"subtask_id":"lift_clear","tcp_end":[0.52915,-0.02739,0.13136],"tcp_start":[0.53333,-0.02753,0.03483],"tcp_to_object_dist_end":0.02177,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62643,0.14656,0.2809],"object_pos_start":[0.54374,-0.02748,0.1152],"object_to_goal_dist_end":0.10579,"object_to_goal_dist_start":0.22084,"object_z_max":0.28075,"peak_contact_force":0.15275,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23713.0,"raw_peak_contact_force":0.17494,"tcp_end":[0.62121,0.14635,0.30768],"tcp_start":[0.52915,-0.02739,0.13136],"tcp_to_object_dist_end":0.02728,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":358.0,"n_steps_budget":1000.0,"object_pos_end":[0.62668,0.16059,0.15551],"object_pos_start":[0.62643,0.14656,0.2809],"object_to_goal_dist_end":0.02269,"object_to_goal_dist_start":0.10579,"object_z_max":0.28094,"peak_contact_force":0.16261,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7104.0,"raw_peak_contact_force":0.29225,"subtask_id":"place","tcp_end":[0.62806,0.16177,0.18859],"tcp_start":[0.62121,0.14635,0.30768],"tcp_to_object_dist_end":0.03313,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62208,0.15864,0.02244],"object_pos_start":[0.62668,0.16059,0.15551],"object_to_goal_dist_end":0.15498,"object_to_goal_dist_start":0.02269,"object_z_max":0.15551,"peak_contact_force":0.15304,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1644.0,"raw_peak_contact_force":1.34778,"tcp_end":[0.62237,0.16011,0.2075],"tcp_start":[0.62806,0.16177,0.18859],"tcp_to_object_dist_end":0.18507,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```