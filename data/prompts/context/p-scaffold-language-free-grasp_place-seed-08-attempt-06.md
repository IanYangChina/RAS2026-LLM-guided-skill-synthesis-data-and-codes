## Search State

- **Seed**: 8
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 12 | -0.0171 | 0.41 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | pose_tolerance | time_limit | 9 | 0.1855 | 0.56 | ✅ accepted |
| 4 | approach → descend → grasp → lift → push → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | time_limit | time_limit | grasp_success | pose_tolerance | pose_tolerance | time_limit | 7 | 0.2678 | 0.54 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.0818 | 0.26 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | 0.0682 | 0.30 | ❌ rejected |

**Proposal policy**: task_score is 0.41 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.017) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_above_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.2
- id: reach_object
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
- id: transport_to_goal
  target_entity: object
  weight: 0.2
- id: hold_at_goal
  target_entity: object
  weight: 0.4
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.12
    orientation:
      mode: none
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_above_object
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: none
  parameters:
    grasp_offset_z:
      type: scalar
      range:
      - -0.01
      - 0.03
      default: 0.005
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    grasp_duration:
      type: scalar
      range:
      - 0.5
      - 3.0
      default: 1.5
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 3
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - -0.005
  subtask_id: reach_object
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: lift_object
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
    - 0.03
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.35
      binds_to:
      - path: generator.speed
        mode: replace
    transport_xy_offset_x:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    transport_xy_offset_y:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    transport_z_offset_delta:
      type: scalar
      range:
      - -0.03
      - 0.07
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: transport_to_goal
- id: hold_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    hold_duration:
      type: scalar
      range:
      - 0.5
      - 3.0
      default: 1.5
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: hold_at_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.12]
  - orientation: mode=none
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings:
    - grasp_offset_z: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_duration: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=3, strategy=offset_target, offset=[0.005, 0.005, -0.005]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_xy_offset_x: status=consumed; consumers=target.offset.x (add)
    - transport_xy_offset_y: status=consumed; consumers=target.offset.y (add)
    - transport_z_offset_delta: status=consumed; consumers=target.offset.z (replace)
- **hold_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - hold_duration: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: -0.017
- **task_score** (E): 0.414
- **fitness_score**: 0.673  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.690

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0968 |
| descend_1 | 1.00 | 1.00 | 0.1597 |
| grasp_1 | 1.00 | 1.00 | 0.0138 |
| lift_1 | 1.00 | 1.00 | 0.1036 |
| transport_1 | 0.00 | 0.00 | 0.0002 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.515, -0.001, 0.212) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 27.543 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.515, -0.001, 0.212)→(0.517, -0.001, 0.053) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 17.041 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.517, -0.001, 0.053)→(0.508, -0.001, 0.042) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.290 | 1.00 / 43.667 | 0.156 | 0.206 |
| lift_1 | lift | 1.00 / step_budget | (0.508, -0.001, 0.042)→(0.516, -0.001, 0.145) | (0.522, -0.001, 0.026)→(0.532, -0.001, 0.123) | 0.290→0.238 | 1.00 / 22.333 | 0.113 | 0.447 |
| transport_1 | approach | 0.00 / guard_failure | (0.563, 0.108, 0.188)→(0.563, 0.109, 0.188) | (0.532, -0.001, 0.123)→(0.581, 0.112, 0.115) | 0.238→0.137 | 0.00 / 0.000 | 0.000 | 0.271 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.598
- phase_score: 0.451
- phase_breakdown.transport_to_goal_score: 0.419
- phase_breakdown.reach_above_object_score: 0.227
- phase_breakdown.reach_object_score: 0.648
- phase_breakdown.lift_object_score: 0.540
- grasp_place_fitness: 0.761

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.761
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.598
- **Median Q (composite search score)**: -0.060
- **K-run variance**: 0.0038
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.288


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89362,"average_solve_count":94.0,"average_success_count":94.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17417,"approach_1.approach_tolerance":0.01242,"descend_1.descend_tolerance":0.02623,"descend_1.grasp_offset_z":0.00282,"grasp_1.grasp_duration":1.89154,"lift_1.lift_height":0.14446,"lift_1.lift_speed":0.68747,"transport_1.min_transport_z":0.09976,"transport_1.transport_speed":0.8419,"transport_1.transport_xy_offset_x":-0.00227,"transport_1.transport_xy_offset_y":-0.01152,"transport_1.transport_z_offset_delta":0.04296},"optimized_scores":{"best_composite_score":-0.06044,"best_fitness_score":0.62956,"best_task_score":0.31762},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.48055,0.04584,-0.00153],"force_p95":0.4124,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49934,"mean_force":0.0952,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46907,0.04602,0.04049]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5018.0,"contact_point_centroid":[0.47343,0.06547,0.09132],"force_p95":0.11094,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30395,"mean_force":0.07192,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47175,0.04622,0.08873]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6504.0,"contact_point_centroid":[0.47483,0.02756,0.09006],"force_p95":0.09731,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28153,"mean_force":0.05788,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47174,0.04622,0.08873]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48282,0.04864,-0.00223],"force_p95":0.18244,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24194,"mean_force":0.13882,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47126,0.04623,0.04004]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1519.0,"contact_point_centroid":[0.49498,0.08925,0.16537],"force_p95":0.13549,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23703,"mean_force":0.10267,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49002,0.07021,0.16399]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1994.0,"contact_point_centroid":[0.49796,0.05398,0.16416],"force_p95":0.13398,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20967,"mean_force":0.08278,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49083,0.07166,0.16492]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5236.0,"contact_point_centroid":[0.47151,0.0271,0.04007],"force_p95":0.06663,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19164,"mean_force":0.04134,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47009,0.04612,0.03885]},{"body_a":"world","body_b":"grasp_target","contact_count":688.0,"contact_point_centroid":[0.4827,0.04873,-0.00181],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49185,0.01772,0.26153]},{"body_a":"world","body_b":"grasp_target","contact_count":1316.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48045,0.04214,0.13482]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4274.0,"contact_point_centroid":[0.4697,0.06549,0.04116],"force_p95":0.08613,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09274,"mean_force":0.05203,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4701,0.04612,0.03886]}],"total_contact_groups":10},"final_pose_error":0.15799,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.53265,0.10151,0.12581],"final_tcp_position":[0.50988,0.10508,0.18684],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":30.79025,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":173.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":30.79025,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":688.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.48388,0.03758,0.22056],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19486,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":329.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1316.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47878,0.04692,0.04803],"tcp_start":[0.48388,0.03758,0.22056],"tcp_to_object_dist_end":0.02243,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48281,0.04723,0.02523],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29143,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.17698,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11310.0,"raw_peak_contact_force":0.24194,"subtask_id":"reach_object","tcp_end":[0.47006,0.04612,0.03882],"tcp_start":[0.47878,0.04692,0.04803],"tcp_to_object_dist_end":0.01866,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":346.0,"n_steps_budget":600.0,"object_pos_end":[0.4948,0.04812,0.13004],"object_pos_start":[0.48281,0.04723,0.02523],"object_to_goal_dist_end":0.22436,"object_to_goal_dist_start":0.29143,"object_z_max":0.12979,"peak_contact_force":0.11569,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11600.0,"raw_peak_contact_force":0.49934,"subtask_id":"lift_object","tcp_end":[0.47774,0.04674,0.15037],"tcp_start":[0.47006,0.04612,0.03882],"tcp_to_object_dist_end":0.02658,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":199.0,"n_steps_budget":1000.0,"object_pos_end":[0.532,0.10113,0.12853],"object_pos_start":[0.4948,0.04812,0.13004],"object_to_goal_dist_end":0.17086,"object_to_goal_dist_start":0.22436,"object_z_max":0.15152,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3513.0,"raw_peak_contact_force":0.23703,"subtask_id":"transport_to_goal","tcp_end":[0.50988,0.10508,0.18684],"tcp_start":[0.50989,0.10493,0.18682],"tcp_to_object_dist_end":0.06249,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.96809,"average_solve_count":94.0,"average_success_count":94.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14626,"approach_1.approach_tolerance":0.02966,"descend_1.descend_tolerance":0.02625,"descend_1.grasp_offset_z":0.00824,"grasp_1.grasp_duration":1.61418,"lift_1.lift_height":0.12935,"lift_1.lift_speed":0.61271,"transport_1.min_transport_z":0.07764,"transport_1.transport_speed":0.39108,"transport_1.transport_xy_offset_x":0.00481,"transport_1.transport_xy_offset_y":-0.00058,"transport_1.transport_z_offset_delta":0.04589},"optimized_scores":{"best_composite_score":-0.06153,"best_fitness_score":0.62847,"best_task_score":0.32566},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.53521,-0.0204,-0.00132],"force_p95":0.38717,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41692,"mean_force":0.07922,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52115,-0.02053,0.04369]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2514.0,"contact_point_centroid":[0.55037,0.00683,0.15445],"force_p95":0.14293,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28459,"mean_force":0.09506,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54444,0.02564,0.15313]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4431.0,"contact_point_centroid":[0.52737,-0.03976,0.08644],"force_p95":0.11003,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27462,"mean_force":0.0749,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52442,-0.02069,0.08387]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5358.0,"contact_point_centroid":[0.52756,-0.00201,0.08437],"force_p95":0.10356,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26971,"mean_force":0.06477,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5243,-0.02069,0.08279]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3111.0,"contact_point_centroid":[0.55207,0.04665,0.15451],"force_p95":0.10823,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17856,"mean_force":0.07907,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54535,0.0285,0.15433]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53704,-0.02134,-0.00206],"force_p95":0.14064,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17629,"mean_force":0.12752,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52334,-0.02055,0.04366]},{"body_a":"world","body_b":"grasp_target","contact_count":884.0,"contact_point_centroid":[0.53702,-0.02132,-0.00185],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12318,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5125,-0.00828,0.24778]},{"body_a":"world","body_b":"grasp_target","contact_count":1048.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52819,-0.01897,0.12355]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5305.0,"contact_point_centroid":[0.52315,-0.0015,0.0446],"force_p95":0.06686,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10878,"mean_force":0.04095,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52211,-0.02054,0.04224]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4178.0,"contact_point_centroid":[0.52311,-0.03984,0.04493],"force_p95":0.08063,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0819,"mean_force":0.05192,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52211,-0.02054,0.04225]}],"total_contact_groups":10},"final_pose_error":0.16243,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.58541,0.09717,0.10422],"final_tcp_position":[0.5657,0.09009,0.18156],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":51.71639,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":222.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":51.71639,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":884.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.52719,-0.01734,0.19318],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1675,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":262.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":50.87667,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1048.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53119,-0.02064,0.05311],"tcp_start":[0.52719,-0.01734,0.19318],"tcp_to_object_dist_end":0.02772,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53695,-0.02104,0.02576],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31667,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13988,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11283.0,"raw_peak_contact_force":0.17629,"subtask_id":"reach_object","tcp_end":[0.52208,-0.02054,0.04221],"tcp_start":[0.53119,-0.02064,0.05311],"tcp_to_object_dist_end":0.02218,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":321.0,"n_steps_budget":600.0,"object_pos_end":[0.54678,-0.02146,0.11423],"object_pos_start":[0.53695,-0.02104,0.02576],"object_to_goal_dist_end":0.27355,"object_to_goal_dist_start":0.31667,"object_z_max":0.114,"peak_contact_force":0.10445,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9871.0,"raw_peak_contact_force":0.41692,"subtask_id":"lift_object","tcp_end":[0.53124,-0.02093,0.13599],"tcp_start":[0.52208,-0.02054,0.04221],"tcp_to_object_dist_end":0.02674,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":298.0,"n_steps_budget":1000.0,"object_pos_end":[0.58492,0.09623,0.10762],"object_pos_start":[0.54678,-0.02146,0.11423],"object_to_goal_dist_end":0.16704,"object_to_goal_dist_start":0.27355,"object_z_max":0.14348,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5625.0,"raw_peak_contact_force":0.28459,"subtask_id":"transport_to_goal","tcp_end":[0.5657,0.09009,0.18156],"tcp_start":[0.56572,0.08986,0.18154],"tcp_to_object_dist_end":0.07664,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.97,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17901,"approach_1.approach_tolerance":0.02346,"descend_1.descend_tolerance":0.0221,"descend_1.grasp_offset_z":0.01186,"grasp_1.grasp_duration":2.0211,"lift_1.lift_height":0.14312,"lift_1.lift_speed":0.53632,"transport_1.min_transport_z":0.07843,"transport_1.transport_speed":0.48561,"transport_1.transport_xy_offset_x":0.01095,"transport_1.transport_xy_offset_y":0.02425,"transport_1.transport_z_offset_delta":0.0455},"optimized_scores":{"best_composite_score":0.07055,"best_fitness_score":0.76055,"best_task_score":0.59801},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.54389,-0.02794,-0.00137],"force_p95":0.33575,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42587,"mean_force":0.07549,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52949,-0.02804,0.04705]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5048.0,"contact_point_centroid":[0.53602,-0.04731,0.09298],"force_p95":0.11105,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33739,"mean_force":0.07397,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5329,-0.02826,0.09071]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4503.0,"contact_point_centroid":[0.57369,0.019,0.16433],"force_p95":0.14683,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29107,"mean_force":0.08755,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56904,0.03755,0.16592]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5676.0,"contact_point_centroid":[0.53641,-0.00958,0.08912],"force_p95":0.11733,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28081,"mean_force":0.06751,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53256,-0.02825,0.08803]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4086.0,"contact_point_centroid":[0.57657,0.0597,0.1646],"force_p95":0.13937,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20216,"mean_force":0.09726,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57092,0.04151,0.16715]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54565,-0.02928,-0.0021],"force_p95":0.15043,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19998,"mean_force":0.13025,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53173,-0.02809,0.04702]},{"body_a":"world","body_b":"grasp_target","contact_count":720.0,"contact_point_centroid":[0.5456,-0.02923,-0.00182],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12331,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51541,-0.01089,0.26218]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5063.0,"contact_point_centroid":[0.53248,-0.00903,0.04708],"force_p95":0.06872,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13573,"mean_force":0.04309,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5305,-0.02806,0.04556]},{"body_a":"world","body_b":"grasp_target","contact_count":1236.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53525,-0.02551,0.1403]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4701.0,"contact_point_centroid":[0.53134,-0.04735,0.04853],"force_p95":0.0823,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08555,"mean_force":0.04878,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53051,-0.02806,0.04557]}],"total_contact_groups":10},"final_pose_error":0.07195,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.62536,0.13959,0.10447],"final_tcp_position":[0.61277,0.13054,0.19456],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.42587,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":181.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":720.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.53302,-0.02286,0.22272],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1972,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":309.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1236.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.5396,-0.02827,0.05675],"tcp_start":[0.53302,-0.02286,0.22272],"tcp_to_object_dist_end":0.03133,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54567,-0.0288,0.02563],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.2608,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14969,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11564.0,"raw_peak_contact_force":0.19998,"subtask_id":"reach_object","tcp_end":[0.53047,-0.02806,0.04553],"tcp_start":[0.5396,-0.02827,0.05675],"tcp_to_object_dist_end":0.02505,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":356.0,"n_steps_budget":600.0,"object_pos_end":[0.55472,-0.02914,0.12376],"object_pos_start":[0.54567,-0.0288,0.02563],"object_to_goal_dist_end":0.21585,"object_to_goal_dist_start":0.2608,"object_z_max":0.12353,"peak_contact_force":0.1174,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10804.0,"raw_peak_contact_force":0.42587,"subtask_id":"lift_object","tcp_end":[0.54023,-0.02862,0.1497],"tcp_start":[0.53047,-0.02806,0.04553],"tcp_to_object_dist_end":0.02972,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":458.0,"n_steps_budget":1000.0,"object_pos_end":[0.62481,0.13864,0.10819],"object_pos_start":[0.55472,-0.02914,0.12376],"object_to_goal_dist_end":0.07403,"object_to_goal_dist_start":0.21585,"object_z_max":0.1519,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8589.0,"raw_peak_contact_force":0.29107,"subtask_id":"transport_to_goal","tcp_end":[0.61277,0.13054,0.19456],"tcp_start":[0.61284,0.13039,0.19459],"tcp_to_object_dist_end":0.08758,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```