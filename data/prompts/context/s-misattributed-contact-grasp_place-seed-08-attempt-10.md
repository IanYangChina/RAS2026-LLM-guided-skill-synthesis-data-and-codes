## Search State

- **Seed**: 8
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14 | -0.0259 | 0.65 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14 | 0.1019 | 0.90 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 10 | 0.3259 | 0.89 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 10 | 0.2579 | 0.76 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 10 | 0.2696 | 0.77 | ❌ rejected |

**Proposal policy**: task_score is 0.65 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.904, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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

## Current Skill (Q=-0.026) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.4
- id: reach_goal
  target_entity: object
  weight: 0.6
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_offset_z:
      type: scalar
      range:
      - 0.0
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
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
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
  subtask_id: reach_object
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.12
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: move_above_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.08
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    above_goal_x:
      type: scalar
      range:
      - -0.06
      - 0.06
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    above_goal_y:
      type: scalar
      range:
      - -0.06
      - 0.06
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: replace
    above_goal_z:
      type: scalar
      range:
      - 0.04
      - 0.12
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: place_at_goal
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    place_x:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    place_y:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: replace
    place_z:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_offset_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **move_above_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.08], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - above_goal_x: status=consumed; consumers=target.offset.x (replace)
    - above_goal_y: status=consumed; consumers=target.offset.y (replace)
    - above_goal_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **place_at_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_x: status=consumed; consumers=target.offset.x (replace)
    - place_y: status=consumed; consumers=target.offset.y (replace)
    - place_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.026
- **task_score** (E): 0.650
- **fitness_score**: 0.794  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.820

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1430 |
| descend_1 | 1.00 | 1.00 | 0.1147 |
| grasp_1 | 1.00 | 1.00 | 0.0133 |
| lift_1 | 1.00 | 1.00 | 0.1163 |
| move_above_goal | 1.00 | 1.00 | 0.2439 |
| place_at_goal | 1.00 | 1.00 | 0.0269 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.515, -0.001, 0.164) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 27.129 | 0.123 |
| descend_1 | descend | 1.00 / step_budget | (0.515, -0.001, 0.164)→(0.517, -0.001, 0.049) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 43.000 | 0.155 | 0.221 |
| grasp_1 | grasp | 1.00 / step_budget | (0.517, -0.001, 0.049)→(0.508, -0.001, 0.039) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.290 | 1.00 / 23.000 | 0.110 | 0.493 |
| lift_1 | lift | 1.00 / step_budget | (0.508, -0.001, 0.039)→(0.516, -0.001, 0.155) | (0.522, -0.001, 0.026)→(0.534, -0.001, 0.138) | 0.290→0.231 | 1.00 / 15.667 | 91007.618 | 0.909 |
| move_above_goal | approach | 1.00 / step_budget | (0.516, -0.001, 0.155)→(0.617, 0.194, 0.250) | (0.534, -0.001, 0.138)→(0.628, 0.187, 0.152) | 0.231→0.093 | 1.00 / 14.000 | 91003.688 | 0.306 |
| place_at_goal | descend | 1.00 / step_budget | (0.617, 0.194, 0.250)→(0.608, 0.198, 0.227) | (0.628, 0.187, 0.152)→(0.619, 0.191, 0.129) | 0.093→0.083 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.868
- phase_score: 0.588
- phase_breakdown.reach_goal_score: 0.632
- phase_breakdown.reach_object_score: 0.522
- grasp_place_fitness: 0.896

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.896
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.868
- **Median Q (composite search score)**: 0.059
- **K-run variance**: 0.0175
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.334


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.288,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11239,"approach_1.speed":0.14835,"descend_1.descend_offset_z":0.00014,"descend_1.speed":0.14367,"lift_1.lift_height":0.19044,"lift_1.speed":0.13462,"move_above_goal.above_goal_x":0.05999,"move_above_goal.above_goal_y":-0.01517,"move_above_goal.above_goal_z":0.07381,"move_above_goal.speed":0.16862,"place_at_goal.place_x":0.00734,"place_at_goal.place_y":-0.002,"place_at_goal.place_z":0.00468,"place_at_goal.speed":0.0734},"optimized_scores":{"best_composite_score":0.05928,"best_fitness_score":0.87928,"best_task_score":0.81081},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":65.0,"contact_point_centroid":[0.48021,0.04627,-0.00167],"force_p95":0.52168,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58091,"mean_force":0.16956,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4694,0.04609,0.03792]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":915.0,"contact_point_centroid":[0.61605,0.22378,0.26147],"force_p95":0.21065,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.385,"mean_force":0.11562,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.6141,0.20604,0.26584]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4699.0,"contact_point_centroid":[0.47431,0.06512,0.10076],"force_p95":0.11302,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33353,"mean_force":0.06829,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4722,0.0461,0.09876]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":916.0,"contact_point_centroid":[0.61524,0.18754,0.26207],"force_p95":0.21287,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32819,"mean_force":0.12034,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.6145,0.20575,0.26645]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4467.0,"contact_point_centroid":[0.47459,0.02715,0.10368],"force_p95":0.11194,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30455,"mean_force":0.07028,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47238,0.04611,0.10128]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48278,0.04847,-0.00222],"force_p95":0.18276,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25562,"mean_force":0.1386,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47176,0.04633,0.03775]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4600.0,"contact_point_centroid":[0.55567,0.10279,0.23504],"force_p95":0.14451,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23699,"mean_force":0.09303,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.55093,0.12151,0.23411]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5300.0,"contact_point_centroid":[0.55521,0.1394,0.23453],"force_p95":0.13446,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23129,"mean_force":0.08329,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.55031,0.12088,0.23367]},{"body_a":"world","body_b":"grasp_target","contact_count":1060.0,"contact_point_centroid":[0.4827,0.04873,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4909,0.01979,0.23158]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4813.0,"contact_point_centroid":[0.47069,0.02702,0.03915],"force_p95":0.07478,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13613,"mean_force":0.04463,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47066,0.04622,0.03664]},{"body_a":"world","body_b":"grasp_target","contact_count":852.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4797,0.04398,0.10329]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5150.0,"contact_point_centroid":[0.47089,0.0656,0.03862],"force_p95":0.07674,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08058,"mean_force":0.04423,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47067,0.04622,0.03665]}],"total_contact_groups":12},"final_pose_error":0.01953,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.60141,0.21633,0.20925],"final_tcp_position":[0.60087,0.21549,0.24596],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.58091,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":266.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":852.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.48225,0.04116,0.16066],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13485,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":213.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.17379,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11763.0,"raw_peak_contact_force":0.25562,"subtask_id":"reach_object","tcp_end":[0.47883,0.04698,0.04524],"tcp_start":[0.48225,0.04116,0.16066],"tcp_to_object_dist_end":0.01968,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48266,0.04681,0.02525],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29173,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.11144,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9231.0,"raw_peak_contact_force":0.58091,"subtask_id":"reach_object","tcp_end":[0.47063,0.04622,0.03661],"tcp_start":[0.47883,0.04698,0.04524],"tcp_to_object_dist_end":0.01656,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":286.0,"n_steps_budget":840.0,"object_pos_end":[0.4972,0.04696,0.17042],"object_pos_start":[0.48266,0.04681,0.02525],"object_to_goal_dist_end":0.20944,"object_to_goal_dist_start":0.29173,"object_z_max":0.16995,"peak_contact_force":0.12726,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9900.0,"raw_peak_contact_force":0.23699,"subtask_id":"reach_object","tcp_end":[0.47839,0.04641,0.18609],"tcp_start":[0.47063,0.04622,0.03661],"tcp_to_object_dist_end":0.02449,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":416.0,"n_steps_budget":1000.0,"object_pos_end":[0.63065,0.19817,0.25191],"object_pos_start":[0.4972,0.04696,0.17042],"object_to_goal_dist_end":0.06148,"object_to_goal_dist_start":0.20944,"object_z_max":0.25175,"peak_contact_force":0.22073,"phase_name":"move_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1831.0,"raw_peak_contact_force":0.385,"subtask_id":"reach_goal","tcp_end":[0.62571,0.19761,0.28517],"tcp_start":[0.47839,0.04641,0.18609],"tcp_to_object_dist_end":0.03363,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":94.0,"n_steps_budget":1000.0,"object_pos_end":[0.60141,0.21633,0.20925],"object_pos_start":[0.63065,0.19817,0.25191],"object_to_goal_dist_end":0.03146,"object_to_goal_dist_start":0.06148,"object_z_max":0.25197,"peak_contact_force":0.12263,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1060.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_goal","tcp_end":[0.60087,0.21549,0.24596],"tcp_start":[0.62571,0.19761,0.28517],"tcp_to_object_dist_end":0.03673,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73881,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10845,"approach_1.speed":0.1,"descend_1.descend_offset_z":0.00154,"descend_1.speed":0.14377,"lift_1.lift_height":0.13495,"lift_1.speed":0.0665,"move_above_goal.above_goal_x":-0.01392,"move_above_goal.above_goal_y":-0.00276,"move_above_goal.above_goal_z":0.05473,"move_above_goal.speed":0.31165,"place_at_goal.place_x":-0.01487,"place_at_goal.place_y":-0.02942,"place_at_goal.place_z":0.01251,"place_at_goal.speed":0.05696},"optimized_scores":{"best_composite_score":-0.21287,"best_fitness_score":0.60713,"best_task_score":0.26991},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":260.0,"contact_point_centroid":[0.6124,0.18088,-0.0063],"force_p95":1.09746,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24268,"mean_force":0.30651,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.58423,0.18598,0.23413]},{"body_a":"world","body_b":"grasp_target","contact_count":72.0,"contact_point_centroid":[0.5348,-0.02021,-0.00153],"force_p95":0.4471,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5006,"mean_force":0.17123,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5214,-0.02046,0.03681]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3532.0,"contact_point_centroid":[0.52626,-0.00132,0.08329],"force_p95":0.10685,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30159,"mean_force":0.06643,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52471,-0.02042,0.08068]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3936.0,"contact_point_centroid":[0.52619,-0.03938,0.08089],"force_p95":0.10195,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28498,"mean_force":0.06144,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52454,-0.02042,0.07914]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2548.0,"contact_point_centroid":[0.55132,0.02447,0.16244],"force_p95":0.15716,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2726,"mean_force":0.09823,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.54566,0.0431,0.16091]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53705,-0.02114,-0.00207],"force_p95":0.14478,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19883,"mean_force":0.12859,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52359,-0.02051,0.03718]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3060.0,"contact_point_centroid":[0.55356,0.06971,0.16618],"force_p95":0.11685,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18419,"mean_force":0.08421,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.54781,0.05137,0.165]},{"body_a":"world","body_b":"grasp_target","contact_count":1148.0,"contact_point_centroid":[0.53702,-0.02132,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51318,-0.00873,0.22919]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4093.0,"contact_point_centroid":[0.52345,-0.00128,0.03853],"force_p95":0.07839,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13131,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52239,-0.02049,0.03582]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.61241,0.18122,-0.00172],"force_p95":0.12211,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12394,"mean_force":0.10668,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.58884,0.20413,0.24172]},{"body_a":"world","body_b":"grasp_target","contact_count":804.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52895,-0.01935,0.10156]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4934.0,"contact_point_centroid":[0.52342,-0.03959,0.0376],"force_p95":0.07052,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08015,"mean_force":0.04467,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52239,-0.02049,0.03582]},{"body_a":"left_finger","body_b":"right_finger","contact_count":59.0,"contact_point_centroid":[0.5881,0.19932,0.24329],"force_p95":0.01627,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01898,"mean_force":0.01433,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.58793,0.19931,0.24105]},{"body_a":"left_finger","body_b":"right_finger","contact_count":87.0,"contact_point_centroid":[0.58927,0.20413,0.24411],"force_p95":0.01242,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01401,"mean_force":0.01148,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.58884,0.20412,0.24175]}],"total_contact_groups":14},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.6124,0.18112,0.01659],"final_tcp_position":[0.5893,0.20379,0.23811],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273022.60802,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":288.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":81.14225,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":804.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52848,-0.01812,0.15617],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13047,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":201.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14053,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10827.0,"raw_peak_contact_force":0.19883,"subtask_id":"reach_object","tcp_end":[0.53126,-0.02063,0.04632],"tcp_start":[0.52848,-0.01812,0.15617],"tcp_to_object_dist_end":0.02111,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53693,-0.0205,0.02574],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31626,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.10915,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7540.0,"raw_peak_contact_force":0.5006,"subtask_id":"reach_object","tcp_end":[0.52236,-0.02048,0.03578],"tcp_start":[0.53126,-0.02063,0.04632],"tcp_to_object_dist_end":0.0177,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.54722,-0.02037,0.11935],"object_pos_start":[0.53693,-0.0205,0.02574],"object_to_goal_dist_end":0.27074,"object_to_goal_dist_start":0.31626,"object_z_max":0.1189,"peak_contact_force":273022.60802,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5927.0,"raw_peak_contact_force":2.24268,"subtask_id":"reach_object","tcp_end":[0.53052,-0.02041,0.13173],"tcp_start":[0.52236,-0.02048,0.03578],"tcp_to_object_dist_end":0.02079,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":413.0,"n_steps_budget":1000.0,"object_pos_end":[0.61245,0.18151,0.0162],"object_pos_start":[0.54722,-0.02037,0.11935],"object_to_goal_dist_end":0.19674,"object_to_goal_dist_start":0.27074,"object_z_max":0.17677,"peak_contact_force":273010.71855,"phase_name":"move_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":171.0,"raw_peak_contact_force":0.12394,"subtask_id":"reach_goal","tcp_end":[0.58887,0.2032,0.24301],"tcp_start":[0.53052,-0.02041,0.13173],"tcp_to_object_dist_end":0.22907,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":21.0,"n_steps_budget":1000.0,"object_pos_end":[0.6124,0.18112,0.01659],"object_pos_start":[0.61245,0.18151,0.0162],"object_to_goal_dist_end":0.19645,"object_to_goal_dist_start":0.19674,"object_z_max":0.01667,"peak_contact_force":0.12263,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1148.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_goal","tcp_end":[0.5893,0.20379,0.23811],"tcp_start":[0.58887,0.2032,0.24301],"tcp_to_object_dist_end":0.22388,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90435,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12898,"approach_1.speed":0.14176,"descend_1.descend_offset_z":0.01148,"descend_1.speed":0.13701,"lift_1.lift_height":0.15157,"lift_1.speed":0.10672,"move_above_goal.above_goal_x":0.0141,"move_above_goal.above_goal_y":0.03782,"move_above_goal.above_goal_z":0.06304,"move_above_goal.speed":0.24493,"place_at_goal.place_x":0.00141,"place_at_goal.place_y":-0.00141,"place_at_goal.place_z":0.00412,"place_at_goal.speed":0.06837},"optimized_scores":{"best_composite_score":0.07587,"best_fitness_score":0.89587,"best_task_score":0.86781},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":429.0,"contact_point_centroid":[0.63935,0.19749,0.20786],"force_p95":0.16756,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40838,"mean_force":0.12549,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.6341,0.17901,0.21261]},{"body_a":"world","body_b":"grasp_target","contact_count":69.0,"contact_point_centroid":[0.54384,-0.02805,-0.00154],"force_p95":0.36117,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39848,"mean_force":0.11743,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52973,-0.02797,0.04668]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3255.0,"contact_point_centroid":[0.53577,-0.00899,0.08973],"force_p95":0.11751,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2704,"mean_force":0.07424,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53277,-0.02803,0.08785]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3777.0,"contact_point_centroid":[0.53577,-0.04696,0.09102],"force_p95":0.11001,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2685,"mean_force":0.06609,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53284,-0.02803,0.08867]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4589.0,"contact_point_centroid":[0.5892,0.05214,0.18109],"force_p95":0.1478,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2487,"mean_force":0.09207,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.58368,0.07057,0.18158]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":450.0,"contact_point_centroid":[0.63972,0.16126,0.20814],"force_p95":0.1333,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24642,"mean_force":0.10426,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.63414,0.17913,0.21299]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4237.0,"contact_point_centroid":[0.58928,0.08952,0.18096],"force_p95":0.14544,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23052,"mean_force":0.09662,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.58383,0.07099,0.18166]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54564,-0.02913,-0.00211],"force_p95":0.15291,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20861,"mean_force":0.1307,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.532,-0.02804,0.04691]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4423.0,"contact_point_centroid":[0.53217,-0.00878,0.04766],"force_p95":0.07581,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14848,"mean_force":0.04882,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53081,-0.02801,0.0455]},{"body_a":"world","body_b":"grasp_target","contact_count":1016.0,"contact_point_centroid":[0.5456,-0.02923,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5166,-0.01183,0.23833]},{"body_a":"world","body_b":"grasp_target","contact_count":868.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53656,-0.02636,0.11604]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5210.0,"contact_point_centroid":[0.53193,-0.04717,0.04759],"force_p95":0.06923,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07119,"mean_force":0.04248,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53081,-0.02801,0.04551]}],"total_contact_groups":12},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.64247,0.17406,0.1603],"final_tcp_position":[0.63284,0.1735,0.19824],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.40838,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":255.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":868.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53537,-0.02455,0.17496],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14937,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":217.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14961,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11433.0,"raw_peak_contact_force":0.20861,"subtask_id":"reach_object","tcp_end":[0.53965,-0.02825,0.05638],"tcp_start":[0.53537,-0.02455,0.17496],"tcp_to_object_dist_end":0.03096,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54555,-0.02839,0.02561],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26055,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.10978,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7101.0,"raw_peak_contact_force":0.39848,"subtask_id":"reach_object","tcp_end":[0.53078,-0.028,0.04547],"tcp_start":[0.53965,-0.02825,0.05638],"tcp_to_object_dist_end":0.02476,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":216.0,"n_steps_budget":780.0,"object_pos_end":[0.5572,-0.02867,0.12552],"object_pos_start":[0.54555,-0.02839,0.02561],"object_to_goal_dist_end":0.21411,"object_to_goal_dist_start":0.26055,"object_z_max":0.12507,"peak_contact_force":0.11841,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8826.0,"raw_peak_contact_force":0.2487,"subtask_id":"reach_object","tcp_end":[0.53949,-0.02819,0.14813],"tcp_start":[0.53078,-0.028,0.04547],"tcp_to_object_dist_end":0.02873,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":411.0,"n_steps_budget":1000.0,"object_pos_end":[0.64118,0.18127,0.1864],"object_pos_start":[0.5572,-0.02867,0.12552],"object_to_goal_dist_end":0.02065,"object_to_goal_dist_start":0.21411,"object_z_max":0.18627,"peak_contact_force":0.12481,"phase_name":"move_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":879.0,"raw_peak_contact_force":0.40838,"subtask_id":"reach_goal","tcp_end":[0.63525,0.18126,0.22295],"tcp_start":[0.53949,-0.02819,0.14813],"tcp_to_object_dist_end":0.03703,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":54.0,"n_steps_budget":1000.0,"object_pos_end":[0.64247,0.17406,0.1603],"object_pos_start":[0.64118,0.18127,0.1864],"object_to_goal_dist_end":0.02127,"object_to_goal_dist_start":0.02065,"object_z_max":0.18644,"peak_contact_force":0.12262,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1016.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_goal","tcp_end":[0.63284,0.1735,0.19824],"tcp_start":[0.63525,0.18126,0.22295],"tcp_to_object_dist_end":0.03915,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```