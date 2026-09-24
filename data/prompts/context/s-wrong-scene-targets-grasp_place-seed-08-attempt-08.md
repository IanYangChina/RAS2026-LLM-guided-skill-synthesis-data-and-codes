## Search State

- **Seed**: 8
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | force_threshold_switch | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 7 | -0.1083 | 0.13 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | contact_detected | time_limit | 5 | 0.0364 | 0.18 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | contact_detected | time_limit | 5 | 0.0399 | 0.19 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | contact_detected | time_limit | 5 | 0.3445 | 0.23 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | force_threshold_switch | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 5 | 0.0935 | 0.15 | ❌ rejected |

**Proposal policy**: task_score is 0.13 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5, 0.0, 0.3)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.48269722766055606, 0.048727684333792556, 0.03)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.48269722766055606, 0.048727684333792556, 0.03]
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
  frozen_object_starts: {'grasp_target': [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]}
  frozen_targets: {'place_target': [0.5, 0.0, 0.3]}
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
| `object` | offset from object initial position (0.5818710838485517, 0.2288548935820029, 0.2304844767544324) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
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

## Current Skill (Q=-0.108) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.1
- id: grasp_success
  anchor: object
  weight: 0.1
- id: lift_clearance
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.1
- id: reach_goal
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.1
- id: place_accuracy
  target_entity: object
  weight: 0.6
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
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
    tolerance: 0.01
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_pre_grasp
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    descend_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: grasp_success
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
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
- id: lift_1
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
    tolerance: 0.01
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
      - path: target.offset.z
        mode: replace
  guards:
  - id: check_lift
    when: after_phase
    predicate: object_lifted
    threshold: 1.0
    on_failure: abort
  subtask_id: lift_clearance
- id: transport_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    transport_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_goal
- id: place_descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_accuracy
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

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - descend_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=check_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=check_lift, when=after_phase, predicate=object_lifted, on_failure=abort, threshold=1.0
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_height: status=consumed; consumers=target.offset.z (replace)
- **place_descend_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.108
- **task_score** (E): 0.128
- **fitness_score**: 0.142  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.500

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.1306 |
| descend_1 | 1.00 | 1.00 | 0.0001 |
| grasp_1 | 1.00 | 1.00 | 0.0000 |
| lift_1 | 0.33 | 1.00 | 0.0455 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.441, -0.002, 0.187) | (0.522, -0.001, 0.030)→(0.483, -0.002, 0.016) | 0.287→0.310 | 1.00 / 5.000 | 247.602 | 1446.090 |
| descend_1 | descend | 1.00 / force_exceeded | (0.441, -0.002, 0.187)→(0.441, -0.002, 0.187) | (0.483, -0.002, 0.016)→(0.483, -0.002, 0.016) | 0.310→0.310 | 1.00 / 5.000 | 416.557 | 267.916 |
| grasp_1 | grasp | 1.00 / step_budget | (0.441, -0.002, 0.186)→(0.441, -0.002, 0.186) | (0.483, -0.002, 0.016)→(0.483, -0.002, 0.016) | 0.310→0.310 | 1.00 / 9.667 | 182025.890 | 365.533 |
| lift_1 | lift | 0.33 / step_budget | (0.441, -0.002, 0.186)→(0.472, -0.012, 0.179) | (0.483, -0.002, 0.016)→(0.483, -0.002, 0.016) | 0.310→0.310 | 1.00 / 10.000 | 244.923 | 965.041 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.125
- phase_score: 0.099
- phase_breakdown.reach_goal_score: 0.000
- phase_breakdown.reach_pre_grasp_score: 0.198
- phase_breakdown.lift_clearance_score: 0.332
- phase_breakdown.place_accuracy_score: 0.000
- phase_breakdown.grasp_success_score: 0.048
- grasp_place_fitness: 0.154

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.154
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.152
- **Median Q (composite search score)**: -0.102
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.367


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
{"anchors":[{"name":"object","value":[0.58187,0.22885,0.23048]},{"name":"goal","value":[0.4827,0.04873,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.67442,"average_solve_count":43.0,"average_success_count":43.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14595,"descend_1.contact_force_threshold":8.51833,"descend_1.descend_z_offset":0.01293,"lift_1.lift_height":0.13038,"place_descend_1.place_force_threshold":4.29714,"place_descend_1.place_z_offset":0.00628,"transport_1.transport_height":0.0965},"optimized_scores":{"best_composite_score":-0.09586,"best_fitness_score":0.15414,"best_task_score":0.12502},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":888.0,"contact_point_centroid":[0.63724,0.01633,-0.00046],"force_p95":219.90635,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1484.323,"mean_force":212.57795,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39789,0.01543,0.12448]},{"body_a":"world","body_b":"link6","contact_count":310.0,"contact_point_centroid":[0.63776,0.03292,-0.00023],"force_p95":324.91494,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":440.09931,"mean_force":227.72839,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.43661,0.03322,0.18399]},{"body_a":"world","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.52883,0.01323,-0.0034],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":303.44467,"mean_force":12.64353,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37765,0.00805,0.04686]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.63135,0.0272,-0.00015],"force_p95":303.17489,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":303.17489,"mean_force":303.17489,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.41166,0.02663,0.16196]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.6318,0.02796,-0.00013],"force_p95":78.2121,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":222.14092,"mean_force":72.61418,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.41192,0.02707,0.16174]},{"body_a":"grasp_target","body_b":"hand","contact_count":46.0,"contact_point_centroid":[0.45885,0.04308,0.03979],"force_p95":3.77132,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.17708,"mean_force":1.64476,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38612,0.00814,0.05159]},{"body_a":"world","body_b":"grasp_target","contact_count":3906.0,"contact_point_centroid":[0.44741,0.0503,-0.00214],"force_p95":0.13816,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.48081,"mean_force":0.13907,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40947,0.01451,0.13444]},{"body_a":"grasp_target","body_b":"link7","contact_count":31.0,"contact_point_centroid":[0.49032,0.02973,0.00999],"force_p95":0.8664,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.87743,"mean_force":0.38512,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37807,0.0081,0.05166]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.4423,0.05052,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.41166,0.02663,0.16196]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.4423,0.05052,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.41192,0.02707,0.16174]},{"body_a":"world","body_b":"grasp_target","contact_count":1240.0,"contact_point_centroid":[0.4423,0.05052,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.43661,0.03322,0.18399]},{"body_a":"left_finger","body_b":"right_finger","contact_count":751.0,"contact_point_centroid":[0.41391,0.02706,0.16037],"force_p95":0.01299,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01096,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.41197,0.02705,0.1616]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1291.0,"contact_point_centroid":[0.43826,0.0332,0.18268],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01285,"mean_force":0.01068,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.43658,0.03321,0.18397]}],"total_contact_groups":13},"final_pose_error":0.04958,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.4423,0.05052,0.01602],"final_tcp_position":[0.4507,0.03722,0.19342],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1484.323,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4423,0.05052,0.01602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.3119,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":212.79458,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4895.0,"raw_peak_contact_force":1484.323,"subtask_id":"reach_pre_grasp","tcp_end":[0.41166,0.02663,0.16196],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15103,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.4423,0.05052,0.01602],"object_pos_start":[0.4423,0.05052,0.01602],"object_to_goal_dist_end":0.3119,"object_to_goal_dist_start":0.3119,"object_z_max":0.01602,"peak_contact_force":388.63227,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":303.17489,"subtask_id":"grasp_success","tcp_end":[0.41167,0.02664,0.16206],"tcp_start":[0.41166,0.02663,0.16196],"tcp_to_object_dist_end":0.15112,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.4423,0.05052,0.01602],"object_pos_start":[0.4423,0.05052,0.01602],"object_to_goal_dist_end":0.3119,"object_to_goal_dist_start":0.3119,"object_z_max":0.01602,"peak_contact_force":69.42783,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3501.0,"raw_peak_contact_force":222.14092,"tcp_end":[0.41198,0.02704,0.1616],"tcp_start":[0.41197,0.02705,0.1616],"tcp_to_object_dist_end":0.15055,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":310.0,"n_steps_budget":600.0,"object_pos_end":[0.4423,0.05052,0.01602],"object_pos_start":[0.4423,0.05052,0.01602],"object_to_goal_dist_end":0.3119,"object_to_goal_dist_start":0.3119,"object_z_max":0.01602,"peak_contact_force":239.30701,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2841.0,"raw_peak_contact_force":440.09931,"subtask_id":"lift_clearance","tcp_end":[0.4507,0.03722,0.19342],"tcp_start":[0.41198,0.02704,0.1616],"tcp_to_object_dist_end":0.1781,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2b35d39beba75b46a5edd8e67b975c00ef2c88fb75a3753bdd32db5918adf9e2`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.61031,0.22775,0.20741]},{"name":"goal","value":[0.53702,-0.02132,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":6.0,"average_failure_rate":0.13333,"average_mean_iterations":33.75556,"average_solve_count":45.0,"average_success_count":39.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11555,"descend_1.contact_force_threshold":9.00046,"descend_1.descend_z_offset":0.01299,"lift_1.lift_height":0.09488,"place_descend_1.place_force_threshold":7.2358,"place_descend_1.place_z_offset":-0.00229,"transport_1.transport_height":0.10226},"optimized_scores":{"best_composite_score":-0.1265,"best_fitness_score":0.1235,"best_task_score":0.106},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.64844,-0.0059,-0.00043],"force_p95":214.81623,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1344.6508,"mean_force":199.62829,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.42067,-0.00611,0.14183]},{"body_a":"world","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.53919,-0.00041,-0.00321],"force_p95":204.9178,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1314.70649,"mean_force":62.83415,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38907,-0.00325,0.04596]},{"body_a":"world","body_b":"link5","contact_count":116.0,"contact_point_centroid":[0.64263,0.11438,-0.00043],"force_p95":630.418,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1201.06804,"mean_force":432.51284,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48514,-0.01983,0.18559]},{"body_a":"world","body_b":"link6","contact_count":110.0,"contact_point_centroid":[0.6737,0.00016,-0.00012],"force_p95":766.35284,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":840.40798,"mean_force":501.11086,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46702,-0.01409,0.18708]},{"body_a":"link5","body_b":"hand","contact_count":351.0,"contact_point_centroid":[0.51821,0.07241,0.12175],"force_p95":196.13265,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":549.12513,"mean_force":86.74129,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48089,-0.0186,0.18349]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.64816,-0.00375,-0.00019],"force_p95":258.64091,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":258.64091,"mean_force":258.64091,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45179,-0.01134,0.19941]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.64845,-0.00375,-0.00013],"force_p95":78.97416,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":126.95412,"mean_force":72.45194,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45201,-0.01129,0.19947]},{"body_a":"grasp_target","body_b":"link7","contact_count":228.0,"contact_point_centroid":[0.51202,-0.02502,0.03746],"force_p95":3.4663,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.26408,"mean_force":0.76571,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4012,-0.00351,0.09128]},{"body_a":"grasp_target","body_b":"hand","contact_count":205.0,"contact_point_centroid":[0.50402,-0.03281,0.05051],"force_p95":1.95972,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.44528,"mean_force":0.75102,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40035,-0.00347,0.08883]},{"body_a":"world","body_b":"grasp_target","contact_count":3538.0,"contact_point_centroid":[0.50733,-0.0252,-0.0025],"force_p95":0.39482,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.39527,"mean_force":0.17006,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43342,-0.00592,0.15515]},{"body_a":"grasp_target","body_b":"link6","contact_count":116.0,"contact_point_centroid":[0.54876,-0.03019,0.02076],"force_p95":0.50031,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.72536,"mean_force":0.24177,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.396,-0.00334,0.08149]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.49914,-0.0259,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45179,-0.01134,0.19941]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.49914,-0.0259,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45201,-0.01129,0.19947]},{"body_a":"world","body_b":"grasp_target","contact_count":1064.0,"contact_point_centroid":[0.49914,-0.0259,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47538,-0.0167,0.18642]},{"body_a":"left_finger","body_b":"right_finger","contact_count":747.0,"contact_point_centroid":[0.45371,-0.01129,0.19775],"force_p95":0.0127,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.011,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45203,-0.0113,0.19939]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1171.0,"contact_point_centroid":[0.47735,-0.01659,0.18482],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01285,"mean_force":0.01014,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47544,-0.01669,0.1863]}],"total_contact_groups":16},"final_pose_error":0.06314,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.49914,-0.0259,0.01602],"final_tcp_position":[0.48183,-0.03279,0.17123],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273004.12075,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49914,-0.0259,0.01602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.33665,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":190.91856,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4999.0,"raw_peak_contact_force":1344.6508,"subtask_id":"reach_pre_grasp","tcp_end":[0.45179,-0.01134,0.19941],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18996,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49914,-0.0259,0.01602],"object_pos_start":[0.49914,-0.0259,0.01602],"object_to_goal_dist_end":0.33665,"object_to_goal_dist_start":0.33665,"object_z_max":0.01602,"peak_contact_force":619.1064,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":258.64091,"subtask_id":"grasp_success","tcp_end":[0.45184,-0.01127,0.19957],"tcp_start":[0.45179,-0.01134,0.19941],"tcp_to_object_dist_end":0.19011,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.49914,-0.0259,0.01602],"object_pos_start":[0.49914,-0.0259,0.01602],"object_to_goal_dist_end":0.33665,"object_to_goal_dist_start":0.33665,"object_z_max":0.01602,"peak_contact_force":273004.12075,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3497.0,"raw_peak_contact_force":126.95412,"tcp_end":[0.45203,-0.0113,0.19938],"tcp_start":[0.45203,-0.0113,0.19939],"tcp_to_object_dist_end":0.18988,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":266.0,"n_steps_budget":660.0,"object_pos_end":[0.49914,-0.0259,0.01602],"object_pos_start":[0.49914,-0.0259,0.01602],"object_to_goal_dist_end":0.33665,"object_to_goal_dist_start":0.33665,"object_z_max":0.01602,"peak_contact_force":254.96533,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2812.0,"raw_peak_contact_force":1201.06804,"subtask_id":"lift_clearance","tcp_end":[0.48183,-0.03279,0.17123],"tcp_start":[0.45203,-0.0113,0.19938],"tcp_to_object_dist_end":0.15633,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `530652a2467d9ac78fab654e7ed7fc5283ca1649270bc8f158e04c16074f9f95`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.63284,0.16493,0.17692]},{"name":"goal","value":[0.5456,-0.02923,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":8.0,"average_failure_rate":0.17778,"average_mean_iterations":42.26667,"average_solve_count":45.0,"average_success_count":37.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14929,"descend_1.contact_force_threshold":12.66777,"descend_1.descend_z_offset":0.02215,"lift_1.lift_height":0.09112,"place_descend_1.place_force_threshold":5.60503,"place_descend_1.place_z_offset":0.01993,"transport_1.transport_height":0.09804},"optimized_scores":{"best_composite_score":-0.1025,"best_fitness_score":0.1475,"best_task_score":0.15225},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.64977,-0.00959,-0.00043],"force_p95":280.3682,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1509.29624,"mean_force":210.22015,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.42676,-0.01069,0.15059]},{"body_a":"world","body_b":"link6","contact_count":74.0,"contact_point_centroid":[0.67864,-0.00428,-0.00012],"force_p95":914.83957,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1253.9557,"mean_force":533.93694,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46918,-0.02064,0.18446]},{"body_a":"world","body_b":"link5","contact_count":98.0,"contact_point_centroid":[0.64386,0.1042,-0.00051],"force_p95":661.1963,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1140.03276,"mean_force":410.64027,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48611,-0.027,0.18755]},{"body_a":"world","body_b":"link6","contact_count":542.0,"contact_point_centroid":[0.6576,-0.01218,-0.00014],"force_p95":88.94583,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":747.50454,"mean_force":74.58191,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45927,-0.02154,0.1975]},{"body_a":"link5","body_b":"hand","contact_count":310.0,"contact_point_centroid":[0.51864,0.06475,0.12318],"force_p95":213.20223,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":612.43125,"mean_force":88.94663,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48129,-0.02525,0.18501]},{"body_a":"world","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.54102,-0.00266,-0.00373],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":318.93854,"mean_force":13.86689,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39005,-0.00535,0.04627]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.65682,-0.012,-0.00021],"force_p95":241.9319,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":241.9319,"mean_force":241.9319,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45937,-0.02149,0.19823]},{"body_a":"grasp_target","body_b":"link7","contact_count":250.0,"contact_point_centroid":[0.5237,-0.02284,0.03554],"force_p95":3.00957,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.13494,"mean_force":0.61544,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40475,-0.00598,0.09907]},{"body_a":"grasp_target","body_b":"hand","contact_count":141.0,"contact_point_centroid":[0.50428,-0.03725,0.04867],"force_p95":2.34538,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.22604,"mean_force":0.93801,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40038,-0.00558,0.08386]},{"body_a":"world","body_b":"grasp_target","contact_count":3646.0,"contact_point_centroid":[0.51435,-0.03036,-0.00225],"force_p95":0.2979,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.36847,"mean_force":0.15612,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43866,-0.01027,0.16245]},{"body_a":"grasp_target","body_b":"link6","contact_count":133.0,"contact_point_centroid":[0.55097,-0.01577,0.02418],"force_p95":0.58809,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.98536,"mean_force":0.35738,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39888,-0.00563,0.08835]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.50792,-0.03057,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45937,-0.02149,0.19823]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.50792,-0.03057,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45928,-0.02154,0.19751]},{"body_a":"world","body_b":"grasp_target","contact_count":848.0,"contact_point_centroid":[0.50792,-0.03057,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47757,-0.02387,0.18629]},{"body_a":"left_finger","body_b":"right_finger","contact_count":751.0,"contact_point_centroid":[0.46094,-0.02152,0.19589],"force_p95":0.01356,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01647,"mean_force":0.01095,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45928,-0.02155,0.19741]},{"body_a":"left_finger","body_b":"right_finger","contact_count":933.0,"contact_point_centroid":[0.47947,-0.0238,0.18479],"force_p95":0.01088,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01246,"mean_force":0.01013,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47753,-0.02385,0.18624]}],"total_contact_groups":16},"final_pose_error":0.07119,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.50792,-0.03057,0.01602],"final_tcp_position":[0.48227,-0.0411,0.17271],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":273004.12079,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50792,-0.03057,0.01602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.28234,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":339.09374,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5080.0,"raw_peak_contact_force":1509.29624,"subtask_id":"reach_pre_grasp","tcp_end":[0.45937,-0.02149,0.19823],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18878,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50792,-0.03057,0.01602],"object_pos_start":[0.50792,-0.03057,0.01602],"object_to_goal_dist_end":0.28234,"object_to_goal_dist_start":0.28234,"object_z_max":0.01602,"peak_contact_force":241.9319,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":241.9319,"subtask_id":"grasp_success","tcp_end":[0.45934,-0.02147,0.19831],"tcp_start":[0.45937,-0.02149,0.19823],"tcp_to_object_dist_end":0.18887,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50792,-0.03057,0.01602],"object_pos_start":[0.50792,-0.03057,0.01602],"object_to_goal_dist_end":0.28234,"object_to_goal_dist_start":0.28234,"object_z_max":0.01602,"peak_contact_force":273004.12079,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3493.0,"raw_peak_contact_force":747.50454,"tcp_end":[0.45928,-0.02156,0.19741],"tcp_start":[0.45928,-0.02156,0.19741],"tcp_to_object_dist_end":0.18802,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":212.0,"n_steps_budget":660.0,"object_pos_end":[0.50792,-0.03057,0.01602],"object_pos_start":[0.50792,-0.03057,0.01602],"object_to_goal_dist_end":0.28234,"object_to_goal_dist_start":0.28234,"object_z_max":0.01602,"peak_contact_force":240.49801,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2263.0,"raw_peak_contact_force":1253.9557,"subtask_id":"lift_clearance","tcp_end":[0.48227,-0.0411,0.17271],"tcp_start":[0.45928,-0.02156,0.19741],"tcp_to_object_dist_end":0.15913,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```