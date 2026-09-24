## Search State

- **Seed**: 8
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | contact_detected | time_limit | 5 | 0.3445 | 0.23 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | force_threshold_switch | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 5 | 0.0935 | 0.15 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | contact_detected | time_limit | 5 | 0.3093 | 0.20 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | contact_detected | time_limit | 6 | 0.1229 | 0.20 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | contact_detected | time_limit | 5 | 0.3416 | 0.23 | ✅ accepted |

**Proposal policy**: task_score is 0.23 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.345) — your mutation base

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

- **Composite score**: 0.345
- **task_score** (E): 0.227
- **fitness_score**: 0.495  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.400

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1445 |
| descend_1 | 1.00 | 1.00 | 0.1505 |
| grasp_1 | 1.00 | 1.00 | 0.0307 |
| lift_1 | 1.00 | 1.00 | 0.1625 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, 0.003, 0.163) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / condition_met | (0.516, 0.003, 0.163)→(0.532, 0.006, 0.028) | (0.522, -0.001, 0.026)→(0.516, 0.009, 0.029) | 0.289→0.282 | 1.00 / 13.000 | 5.296 | 717.143 |
| grasp_1 | grasp | 1.00 / step_budget | (0.532, 0.006, 0.028)→(0.521, 0.002, 0.005) | (0.516, 0.009, 0.029)→(0.514, 0.018, 0.019) | 0.282→0.283 | 1.00 / 31.000 | 62.254 | 456.952 |
| lift_1 | lift | 1.00 / step_budget | (0.521, 0.002, 0.005)→(0.511, 0.015, 0.165) | (0.514, 0.018, 0.019)→(0.510, 0.027, 0.123) | 0.283→0.225 | 1.00 / 29.333 | 91002.613 | 76.447 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.272
- phase_score: 0.204
- phase_breakdown.reach_goal_score: 0.000
- phase_breakdown.reach_pre_grasp_score: 0.762
- phase_breakdown.lift_clearance_score: 0.658
- phase_breakdown.place_accuracy_score: 0.000
- phase_breakdown.grasp_success_score: 0.617
- grasp_place_fitness: 0.629

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.629
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.272
- **Median Q (composite search score)**: 0.448
- **K-run variance**: 0.0284
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.328


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.21622,"average_solve_count":74.0,"average_success_count":74.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12689,"descend_1.descend_z_offset":0.02011,"lift_1.lift_height":0.19998,"place_descend_1.place_z_offset":0.00506,"transport_1.transport_height":0.18839},"optimized_scores":{"best_composite_score":0.47869,"best_fitness_score":0.62869,"best_task_score":0.27248},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":40.0,"contact_point_centroid":[0.5482,0.09747,-0.00501],"force_p95":1064.48648,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1223.42872,"mean_force":279.16777,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50133,0.06099,-0.01088]},{"body_a":"world","body_b":"link7","contact_count":41.0,"contact_point_centroid":[0.61838,0.05352,-0.00062],"force_p95":342.60864,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":392.46387,"mean_force":281.92507,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49588,0.06248,-0.00159]},{"body_a":"world","body_b":"link7","contact_count":450.0,"contact_point_centroid":[0.60455,0.05812,-0.00017],"force_p95":98.67773,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":214.32213,"mean_force":80.28018,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48295,0.0695,0.01757]},{"body_a":"world","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.60451,0.05809,-0.00012],"force_p95":142.65499,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":149.02927,"mean_force":97.85857,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48292,0.06945,0.0177]},{"body_a":"world","body_b":"left_finger","contact_count":670.0,"contact_point_centroid":[0.50018,0.01931,-0.00836],"force_p95":12.26979,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":44.2695,"mean_force":4.20617,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50098,0.06107,-0.00909]},{"body_a":"world","body_b":"right_finger","contact_count":697.0,"contact_point_centroid":[0.50578,0.1025,-0.00901],"force_p95":10.81316,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":34.75927,"mean_force":4.39744,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50043,0.0611,-0.00868]},{"body_a":"world","body_b":"grasp_target","contact_count":221.0,"contact_point_centroid":[0.47992,0.07486,-0.00251],"force_p95":0.45332,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.80488,"mean_force":0.14823,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48112,0.06917,0.02235]},{"body_a":"world","body_b":"grasp_target","contact_count":1759.0,"contact_point_centroid":[0.48305,0.05616,-0.00295],"force_p95":0.49582,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61953,"mean_force":0.2309,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48296,0.0695,0.01757]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":22.0,"contact_point_centroid":[0.47882,0.02909,0.01461],"force_p95":0.40343,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.48784,"mean_force":0.21417,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48554,0.06768,0.01509]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5921.0,"contact_point_centroid":[0.48211,0.04229,0.01497],"force_p95":0.14225,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32211,"mean_force":0.06334,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48296,0.06948,0.01758]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19383.0,"contact_point_centroid":[0.48002,0.04984,0.0996],"force_p95":0.09368,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31181,"mean_force":0.05336,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47952,0.06919,0.09955]},{"body_a":"world","body_b":"grasp_target","contact_count":544.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27006,"mean_force":0.12471,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50912,0.05768,0.05978]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19418.0,"contact_point_centroid":[0.48271,0.08833,0.10027],"force_p95":0.09212,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25594,"mean_force":0.04935,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47951,0.06918,0.09958]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2411.0,"contact_point_centroid":[0.48648,0.08993,0.02265],"force_p95":0.14535,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22598,"mean_force":0.0862,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48293,0.06947,0.0176]},{"body_a":"world","body_b":"grasp_target","contact_count":1780.0,"contact_point_centroid":[0.4827,0.04873,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49012,0.03037,0.23706]}],"total_contact_groups":15},"final_pose_error":0.04176,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.48592,0.06896,0.17336],"final_tcp_position":[0.48047,0.06952,0.18047],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1223.42872,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":446.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1780.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.48084,0.04821,0.16653],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14052,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":136.0,"n_steps_budget":1000.0,"object_pos_end":[0.48255,0.04915,0.02648],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28945,"object_to_goal_dist_start":0.28998,"object_z_max":0.02633,"peak_contact_force":3.6222,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2014.0,"raw_peak_contact_force":1223.42872,"subtask_id":"grasp_success","tcp_end":[0.4844,0.06835,0.0161],"tcp_start":[0.48084,0.04821,0.16653],"tcp_to_object_dist_end":0.02191,"terminated_normally":true,"termination_reason":"condition_met"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48355,0.06994,0.02213],"object_pos_start":[0.48255,0.04915,0.02648],"object_to_goal_dist_end":0.27988,"object_to_goal_dist_start":0.28945,"object_z_max":0.0273,"peak_contact_force":78.64717,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10541.0,"raw_peak_contact_force":214.32213,"tcp_end":[0.48292,0.06947,0.0176],"tcp_start":[0.4844,0.06835,0.0161],"tcp_to_object_dist_end":0.0046,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48592,0.06896,0.17336],"object_pos_start":[0.48355,0.06994,0.02213],"object_to_goal_dist_end":0.19503,"object_to_goal_dist_start":0.27988,"object_z_max":0.1732,"peak_contact_force":0.0793,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39027.0,"raw_peak_contact_force":149.02927,"subtask_id":"lift_clearance","tcp_end":[0.48047,0.06952,0.18047],"tcp_start":[0.48292,0.06947,0.0176],"tcp_to_object_dist_end":0.00898,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.32836,"average_solve_count":67.0,"average_success_count":67.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1674,"descend_1.descend_z_offset":0.03015,"lift_1.lift_height":0.18985,"place_descend_1.place_z_offset":-0.01943,"transport_1.transport_height":0.17033},"optimized_scores":{"best_composite_score":0.44819,"best_fitness_score":0.59819,"best_task_score":0.2366},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":117.0,"contact_point_centroid":[0.62199,0.02432,-0.00208],"force_p95":507.78323,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":925.06235,"mean_force":213.46915,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.56231,0.0021,-0.01128]},{"body_a":"world","body_b":"hand","contact_count":422.0,"contact_point_centroid":[0.6067,0.06195,-0.00016],"force_p95":81.31843,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":203.2729,"mean_force":68.34782,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51161,0.03305,0.00963]},{"body_a":"world","body_b":"hand","contact_count":6.0,"contact_point_centroid":[0.60667,0.06255,-0.00011],"force_p95":46.69867,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":47.54618,"mean_force":33.58841,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51159,0.03362,0.0097]},{"body_a":"world","body_b":"left_finger","contact_count":1414.0,"contact_point_centroid":[0.56763,-0.04085,-0.01048],"force_p95":18.95221,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":36.4299,"mean_force":12.52169,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.56619,-0.00051,-0.01181]},{"body_a":"world","body_b":"right_finger","contact_count":1517.0,"contact_point_centroid":[0.56428,0.04003,-0.01024],"force_p95":10.43459,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":32.23308,"mean_force":6.64579,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.56247,0.00058,-0.01094]},{"body_a":"world","body_b":"right_finger","contact_count":230.0,"contact_point_centroid":[0.52987,0.05239,-0.00123],"force_p95":3.12581,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.91659,"mean_force":0.99262,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51061,0.03372,0.01177]},{"body_a":"world","body_b":"right_finger","contact_count":3465.0,"contact_point_centroid":[0.53424,0.05217,-0.00194],"force_p95":1.45986,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.69097,"mean_force":0.91429,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51165,0.03307,0.00975]},{"body_a":"world","body_b":"grasp_target","contact_count":450.0,"contact_point_centroid":[0.5237,0.01781,-0.00688],"force_p95":0.59276,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.45921,"mean_force":0.48343,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51167,0.03313,0.00981]},{"body_a":"world","body_b":"grasp_target","contact_count":823.0,"contact_point_centroid":[0.53706,-0.02044,-0.00191],"force_p95":0.6923,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.36501,"mean_force":0.18378,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.57747,-0.00335,0.04772]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":173.0,"contact_point_centroid":[0.51591,-0.03407,0.00298],"force_p95":0.78878,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.14601,"mean_force":0.33028,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53341,0.00124,-0.00657]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3417.0,"contact_point_centroid":[0.49428,0.00859,0.0109],"force_p95":0.16344,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.94883,"mean_force":0.07208,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51172,0.03327,0.00994]},{"body_a":"grasp_target","body_b":"hand","contact_count":447.0,"contact_point_centroid":[0.54337,0.00687,0.0187],"force_p95":0.37742,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.82842,"mean_force":0.18356,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51167,0.03313,0.00981]},{"body_a":"grasp_target","body_b":"hand","contact_count":48.0,"contact_point_centroid":[0.54284,-0.02611,0.03479],"force_p95":0.62767,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.68917,"mean_force":0.43101,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52677,0.00689,-0.00314]},{"body_a":"world","body_b":"grasp_target","contact_count":93.0,"contact_point_centroid":[0.52681,0.01704,-0.00312],"force_p95":0.43951,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67726,"mean_force":0.16247,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50936,0.034,0.01545]},{"body_a":"grasp_target","body_b":"hand","contact_count":485.0,"contact_point_centroid":[0.54307,0.01691,0.05963],"force_p95":0.19005,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42075,"mean_force":0.07755,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50843,0.035,0.04619]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15170.0,"contact_point_centroid":[0.52498,0.05063,0.09771],"force_p95":0.1551,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27009,"mean_force":0.0717,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50984,0.03625,0.09948]}],"total_contact_groups":19},"final_pose_error":0.04099,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.51183,0.03903,0.16962],"final_tcp_position":[0.51209,0.03782,0.16927],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":925.06235,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":362.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1444.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.52995,-0.01561,0.20114],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17536,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":235.0,"n_steps_budget":1000.0,"object_pos_end":[0.51922,0.00737,0.03492],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.29431,"object_to_goal_dist_start":0.31672,"object_z_max":0.03469,"peak_contact_force":9.32823,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4092.0,"raw_peak_contact_force":925.06235,"subtask_id":"grasp_success","tcp_end":[0.51207,0.02574,0.00768],"tcp_start":[0.52995,-0.01561,0.20114],"tcp_to_object_dist_end":0.03362,"terminated_normally":true,"termination_reason":"condition_met"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5163,0.03856,0.02019],"object_pos_start":[0.51922,0.00737,0.03492],"object_to_goal_dist_end":0.28228,"object_to_goal_dist_start":0.29431,"object_z_max":0.03716,"peak_contact_force":66.10902,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10089.0,"raw_peak_contact_force":203.2729,"tcp_end":[0.51164,0.03362,0.0096],"tcp_start":[0.51207,0.02574,0.00768],"tcp_to_object_dist_end":0.01258,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51183,0.03903,0.16962],"object_pos_start":[0.5163,0.03856,0.02019],"object_to_goal_dist_end":0.21621,"object_to_goal_dist_start":0.28228,"object_z_max":0.16941,"peak_contact_force":0.12293,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29791.0,"raw_peak_contact_force":47.54618,"subtask_id":"lift_clearance","tcp_end":[0.51209,0.03782,0.16927],"tcp_start":[0.51164,0.03362,0.0096],"tcp_to_object_dist_end":0.00128,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":19.0,"average_failure_rate":0.19588,"average_mean_iterations":42.4433,"average_solve_count":97.0,"average_success_count":78.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08823,"descend_1.descend_z_offset":0.01608,"lift_1.lift_height":0.16508,"place_descend_1.place_z_offset":0.01848,"transport_1.transport_height":0.15775},"optimized_scores":{"best_composite_score":0.10667,"best_fitness_score":0.25667,"best_task_score":0.1728},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":395.0,"contact_point_centroid":[0.5318,-0.00302,-0.00035],"force_p95":59.17918,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":953.26139,"mean_force":54.3676,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.56817,-0.09677,-0.01357]},{"body_a":"world","body_b":"right_finger","contact_count":4354.0,"contact_point_centroid":[0.54531,-0.07124,-0.01315],"force_p95":6.02641,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":40.33062,"mean_force":4.32635,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.56829,-0.0967,-0.01328]},{"body_a":"world","body_b":"hand","contact_count":4.0,"contact_point_centroid":[0.53187,-0.00323,-8e-05],"force_p95":31.87048,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":32.76498,"mean_force":20.17285,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.56813,-0.09703,-0.013]},{"body_a":"world","body_b":"left_finger","contact_count":4334.0,"contact_point_centroid":[0.59329,-0.12072,-0.00837],"force_p95":4.65512,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":22.36283,"mean_force":3.47916,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.56824,-0.09671,-0.01336]},{"body_a":"world","body_b":"right_finger","contact_count":1226.0,"contact_point_centroid":[0.54362,-0.07125,-0.00521],"force_p95":4.0879,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":8.10026,"mean_force":1.90092,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.56503,-0.09531,-0.00199]},{"body_a":"world","body_b":"left_finger","contact_count":1014.0,"contact_point_centroid":[0.58968,-0.11848,-0.00421],"force_p95":3.8956,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5.49178,"mean_force":2.03174,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.56551,-0.09561,-0.0033]},{"body_a":"grasp_target","body_b":"hand","contact_count":439.0,"contact_point_centroid":[0.55701,-0.02547,0.0109],"force_p95":0.83288,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.05013,"mean_force":0.70365,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.56843,-0.09666,-0.01305]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2140.0,"contact_point_centroid":[0.54665,-0.06938,-0.00398],"force_p95":0.36424,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.70205,"mean_force":0.1262,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.56893,-0.09655,-0.01243]},{"body_a":"world","body_b":"grasp_target","contact_count":1185.0,"contact_point_centroid":[0.54043,-0.0438,-0.00646],"force_p95":1.37022,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.18338,"mean_force":0.48132,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5695,-0.09615,-0.01078]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1.0,"contact_point_centroid":[0.56546,-0.03957,0.05498],"force_p95":2.93839,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.93839,"mean_force":2.93839,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.59803,-0.07414,0.06282]},{"body_a":"world","body_b":"grasp_target","contact_count":180.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.90394,"mean_force":0.13206,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5696,-0.04321,0.10327]},{"body_a":"grasp_target","body_b":"hand","contact_count":278.0,"contact_point_centroid":[0.55091,-0.03134,0.0342],"force_p95":0.52337,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.80345,"mean_force":0.30685,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.56152,-0.09221,0.00896]},{"body_a":"world","body_b":"grasp_target","contact_count":3093.0,"contact_point_centroid":[0.5323,-0.02918,-0.00224],"force_p95":0.32592,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65279,"mean_force":0.14978,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.55047,-0.07583,0.07899]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1506.0,"contact_point_centroid":[0.5445,-0.07014,0.01321],"force_p95":0.26987,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39897,"mean_force":0.09696,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.56307,-0.09366,0.00394]},{"body_a":"world","body_b":"grasp_target","contact_count":2476.0,"contact_point_centroid":[0.5456,-0.02923,-0.00194],"force_p95":0.13057,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51861,-0.00117,0.20812]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2748.0,"contact_point_centroid":[0.54899,-0.07105,0.09632],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01641,"mean_force":0.0103,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.54797,-0.07213,0.09484]}],"total_contact_groups":16},"final_pose_error":0.03542,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.53333,-0.02657,0.02602],"final_tcp_position":[0.54152,-0.06103,0.14568],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":273007.63552,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":620.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2476.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.53869,-0.02335,0.12239],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09679,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":45.0,"n_steps_budget":1000.0,"object_pos_end":[0.54558,-0.02937,0.02592],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26109,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":2.93839,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":181.0,"raw_peak_contact_force":2.93839,"subtask_id":"grasp_success","tcp_end":[0.59805,-0.07608,0.05975],"tcp_start":[0.53869,-0.02335,0.12239],"tcp_to_object_dist_end":0.07797,"terminated_normally":true,"termination_reason":"condition_met"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54161,-0.05454,0.01542],"object_pos_start":[0.54558,-0.02937,0.02592],"object_to_goal_dist_end":0.28735,"object_to_goal_dist_start":0.26109,"object_z_max":0.02592,"peak_contact_force":42.00584,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12847.0,"raw_peak_contact_force":953.26139,"tcp_end":[0.56813,-0.09705,-0.01303],"tcp_start":[0.59805,-0.07608,0.05975],"tcp_to_object_dist_end":0.05762,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53333,-0.02657,0.02602],"object_pos_start":[0.54161,-0.05454,0.01542],"object_to_goal_dist_end":0.26334,"object_to_goal_dist_start":0.28735,"object_z_max":0.03569,"peak_contact_force":273007.63552,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9869.0,"raw_peak_contact_force":32.76498,"subtask_id":"lift_clearance","tcp_end":[0.54152,-0.06103,0.14568],"tcp_start":[0.56813,-0.09705,-0.01303],"tcp_to_object_dist_end":0.12479,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```