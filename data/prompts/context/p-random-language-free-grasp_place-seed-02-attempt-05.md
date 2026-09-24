## Search State

- **Seed**: 2
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 13 | 0.2158 | 0.95 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 14 | -0.5429 | 0.16 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 11 | 0.2720 | 0.87 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 11 | 0.3386 | 1.00 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | impedance_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | contact_detected | time_limit | pose_tolerance | 15 | -0.2570 | 0.39 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.95). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 1.000, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.216) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.3
- id: reach_goal
  weight: 0.7
phases:
- id: approach_object
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
    - 0.12
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    approach_offset_z:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: reach_object
- id: descend_grasp
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_offset_z:
      type: scalar
      range:
      - 0.0
      - 0.04
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
- id: grasp
  type: grasp
  control: impedance_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: none
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
    - 0.15
    tolerance: 0.03
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
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
    tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
- id: place_at_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    place_offset_z:
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
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.12], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_offset_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
    - tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_offset_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
    - tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **place_at_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
    - tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: 0.216
- **task_score** (E): 0.952
- **fitness_score**: 0.956  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.740

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1316 |
| descend_grasp | 1.00 | 1.00 | 0.1396 |
| grasp | 1.00 | 1.00 | 0.0122 |
| lift | 1.00 | 1.00 | 0.1122 |
| place_at_goal | 1.00 | 1.00 | 0.2348 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.492, -0.012, 0.174) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.492, -0.012, 0.174)→(0.489, -0.015, 0.034) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.489, -0.015, 0.034)→(0.480, -0.015, 0.025) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 43.667 | 0.138 | 0.193 |
| lift | lift | 1.00 / step_budget | (0.480, -0.015, 0.025)→(0.477, -0.015, 0.138) | (0.493, -0.015, 0.026)→(0.494, -0.015, 0.135) | 0.281→0.241 | 1.00 / 31.000 | 0.097 | 0.756 |
| place_at_goal | approach | 1.00 / step_budget | (0.477, -0.015, 0.138)→(0.624, 0.164, 0.165) | (0.494, -0.015, 0.135)→(0.635, 0.164, 0.149) | 0.241→0.020 | 1.00 / 29.667 | 0.099 | 0.215 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.023
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.761
- phase_breakdown.reach_goal_score: 0.699
- phase_breakdown.grasp_lift_score: 1.000
- phase_breakdown.reach_object_score: 0.558
- grasp_place_fitness: 0.983

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.983
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.236
- **K-run variance**: 0.0011
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.340


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.16667,"average_solve_count":96.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.09892,"approach_object.speed":0.11136,"approach_object.tolerance":0.03331,"descend_grasp.descend_offset_z":-0.00409,"descend_grasp.speed":0.15956,"descend_grasp.tolerance":0.00962,"grasp.guard_grasp_check_threshold":0.00293,"lift.lift_height":0.14953,"lift.speed":0.13843,"lift.tolerance":0.03125,"place_at_goal.place_offset_z":0.009,"place_at_goal.speed":0.27207,"place_at_goal.tolerance":0.02546},"optimized_scores":{"best_composite_score":0.16901,"best_fitness_score":0.90901,"best_task_score":0.85746},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.47315,-0.01905,-0.00145],"force_p95":0.7949,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.8337,"mean_force":0.27658,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4628,-0.01945,0.02393]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7188.0,"contact_point_centroid":[0.54663,0.04941,0.16567],"force_p95":0.11939,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33865,"mean_force":0.08375,"phase_index":4.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.54232,0.06815,0.16453]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3547.0,"contact_point_centroid":[0.46303,-0.00032,0.07598],"force_p95":0.11129,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3378,"mean_force":0.06797,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46127,-0.0194,0.07338]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3875.0,"contact_point_centroid":[0.46309,-0.0384,0.07496],"force_p95":0.10638,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32792,"mean_force":0.06347,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46126,-0.0194,0.0731]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7782.0,"contact_point_centroid":[0.54891,0.08842,0.16618],"force_p95":0.11213,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23761,"mean_force":0.07836,"phase_index":4.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.54395,0.06988,0.165]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.01997,-0.00205],"force_p95":0.1392,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19266,"mean_force":0.12735,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46525,-0.0195,0.02382]},{"body_a":"world","body_b":"grasp_target","contact_count":788.0,"contact_point_centroid":[0.47616,-0.02015,-0.00184],"force_p95":0.13748,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12325,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48978,-0.0076,0.23167]},{"body_a":"world","body_b":"grasp_target","contact_count":1548.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47407,-0.01778,0.09315]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5049.0,"contact_point_centroid":[0.4638,-0.00026,0.02531],"force_p95":0.06594,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09361,"mean_force":0.04286,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46412,-0.01948,0.02273]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5174.0,"contact_point_centroid":[0.46404,-0.03874,0.0247],"force_p95":0.06673,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08628,"mean_force":0.0431,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46412,-0.01948,0.02273]}],"total_contact_groups":10},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.63079,0.14897,0.16935],"final_tcp_position":[0.61901,0.14885,0.18758],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.8337,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":198.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":788.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47888,-0.01599,0.15832],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1324,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":387.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1548.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47195,-0.01964,0.03045],"tcp_start":[0.47888,-0.01599,0.15832],"tcp_to_object_dist_end":0.00613,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47602,-0.0195,0.0258],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28818,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.1366,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12023.0,"raw_peak_contact_force":0.19266,"subtask_id":"grasp_lift","tcp_end":[0.46409,-0.01947,0.0227],"tcp_start":[0.47195,-0.01964,0.03045],"tcp_to_object_dist_end":0.01232,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":223.0,"n_steps_budget":690.0,"object_pos_end":[0.48146,-0.01923,0.14117],"object_pos_start":[0.47602,-0.0195,0.0258],"object_to_goal_dist_end":0.23814,"object_to_goal_dist_start":0.28818,"object_z_max":0.14068,"peak_contact_force":0.10655,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7482.0,"raw_peak_contact_force":0.8337,"tcp_end":[0.46132,-0.01937,0.14237],"tcp_start":[0.46409,-0.01947,0.0227],"tcp_to_object_dist_end":0.02017,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":592.0,"n_steps_budget":1000.0,"object_pos_end":[0.63079,0.14897,0.16935],"object_pos_start":[0.48146,-0.01923,0.14117],"object_to_goal_dist_end":0.02307,"object_to_goal_dist_start":0.23814,"object_z_max":0.16931,"peak_contact_force":0.11357,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14970.0,"raw_peak_contact_force":0.33865,"subtask_id":"reach_goal","tcp_end":[0.61901,0.14885,0.18758],"tcp_start":[0.46132,-0.01937,0.14237],"tcp_to_object_dist_end":0.02171,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.21212,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.11955,"approach_object.speed":0.15546,"approach_object.tolerance":0.02901,"descend_grasp.descend_offset_z":-0.00835,"descend_grasp.speed":0.16494,"descend_grasp.tolerance":0.01648,"grasp.guard_grasp_check_threshold":0.00233,"lift.lift_height":0.12577,"lift.speed":0.12774,"lift.tolerance":0.02441,"place_at_goal.place_offset_z":0.00937,"place_at_goal.speed":0.08997,"place_at_goal.tolerance":0.02108},"optimized_scores":{"best_composite_score":0.24267,"best_fitness_score":0.98267,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.45569,-0.02508,-0.00156],"force_p95":0.72991,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.80111,"mean_force":0.26696,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44636,-0.02512,0.02716]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3607.0,"contact_point_centroid":[0.44563,-0.04418,0.07239],"force_p95":0.08879,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34243,"mean_force":0.05632,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44494,-0.02505,0.07056]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3346.0,"contact_point_centroid":[0.44559,-0.00589,0.07205],"force_p95":0.09655,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34037,"mean_force":0.05994,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44495,-0.02505,0.06965]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.0261,-0.0021],"force_p95":0.15281,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22645,"mean_force":0.13089,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44877,-0.0252,0.02705]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11171.0,"contact_point_centroid":[0.53781,0.07214,0.11786],"force_p95":0.10526,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1696,"mean_force":0.07655,"phase_index":4.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.53389,0.09083,0.11678]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11459.0,"contact_point_centroid":[0.54082,0.11308,0.11751],"force_p95":0.10585,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14833,"mean_force":0.07376,"phase_index":4.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.53676,0.09447,0.1167]},{"body_a":"world","body_b":"grasp_target","contact_count":676.0,"contact_point_centroid":[0.45856,-0.02632,-0.00181],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12335,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48358,-0.00974,0.24091]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4782.0,"contact_point_centroid":[0.44788,-0.00599,0.02798],"force_p95":0.07139,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13534,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4477,-0.02517,0.02605]},{"body_a":"world","body_b":"grasp_target","contact_count":1192.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.45968,-0.02289,0.10527]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4974.0,"contact_point_centroid":[0.4479,-0.04442,0.02792],"force_p95":0.07182,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08727,"mean_force":0.04483,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4477,-0.02517,0.02606]}],"total_contact_groups":10},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.63043,0.19563,0.09916],"final_tcp_position":[0.61715,0.19587,0.11465],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.80111,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":170.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":676.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.46582,-0.02047,0.17763],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15189,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":298.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1192.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45555,-0.02542,0.03363],"tcp_start":[0.46582,-0.02047,0.17763],"tcp_to_object_dist_end":0.00823,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02525,0.02563],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30301,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14828,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11556.0,"raw_peak_contact_force":0.22645,"subtask_id":"grasp_lift","tcp_end":[0.44767,-0.02516,0.02603],"tcp_start":[0.45555,-0.02542,0.03363],"tcp_to_object_dist_end":0.01078,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":179.0,"n_steps_budget":630.0,"object_pos_end":[0.46202,-0.02496,0.11903],"object_pos_start":[0.45844,-0.02525,0.02563],"object_to_goal_dist_end":0.2875,"object_to_goal_dist_start":0.30301,"object_z_max":0.11853,"peak_contact_force":0.1004,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7013.0,"raw_peak_contact_force":0.80111,"tcp_end":[0.44491,-0.02501,0.12196],"tcp_start":[0.44767,-0.02516,0.02603],"tcp_to_object_dist_end":0.01736,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":828.0,"n_steps_budget":1000.0,"object_pos_end":[0.63043,0.19563,0.09916],"object_pos_start":[0.46202,-0.02496,0.11903],"object_to_goal_dist_end":0.01955,"object_to_goal_dist_start":0.2875,"object_z_max":0.12021,"peak_contact_force":0.10384,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22630.0,"raw_peak_contact_force":0.1696,"subtask_id":"reach_goal","tcp_end":[0.61715,0.19587,0.11465],"tcp_start":[0.44491,-0.02501,0.12196],"tcp_to_object_dist_end":0.0204,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88235,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.12776,"approach_object.speed":0.17479,"approach_object.tolerance":0.02128,"descend_grasp.descend_offset_z":-0.00875,"descend_grasp.speed":0.22424,"descend_grasp.tolerance":0.02246,"grasp.guard_grasp_check_threshold":0.00137,"lift.lift_height":0.15057,"lift.speed":0.05224,"lift.tolerance":0.01066,"place_at_goal.place_offset_z":0.01554,"place_at_goal.speed":0.28099,"place_at_goal.tolerance":0.03379},"optimized_scores":{"best_composite_score":0.23558,"best_fitness_score":0.97558,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":73.0,"contact_point_centroid":[0.54017,0.00043,-0.0015],"force_p95":0.60284,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63465,"mean_force":0.29913,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52786,0.0008,0.02864]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4612.0,"contact_point_centroid":[0.52623,-0.01843,0.08651],"force_p95":0.08432,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31316,"mean_force":0.06137,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52557,0.00076,0.08374]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5326.0,"contact_point_centroid":[0.5261,0.0198,0.08662],"force_p95":0.07848,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30077,"mean_force":0.0548,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52556,0.00076,0.08463]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00099,-0.00203],"force_p95":0.13233,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16053,"mean_force":0.12538,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5301,0.00085,0.02908]},{"body_a":"world","body_b":"grasp_target","contact_count":652.0,"contact_point_centroid":[0.54431,0.00113,-0.0018],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12338,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51522,0.00041,0.24434]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10446.0,"contact_point_centroid":[0.58387,0.09786,0.17278],"force_p95":0.07543,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13729,"mean_force":0.05052,"phase_index":4.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.58364,0.07888,0.17103]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8840.0,"contact_point_centroid":[0.58125,0.05618,0.17235],"force_p95":0.08258,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13583,"mean_force":0.0584,"phase_index":4.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.58098,0.07535,0.16994]},{"body_a":"world","body_b":"grasp_target","contact_count":928.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53414,0.0009,0.11178]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53025,-0.01837,0.03036],"force_p95":0.07614,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11409,"mean_force":0.0517,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52888,0.00083,0.02771]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53013,0.01991,0.02948],"force_p95":0.06822,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09675,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52888,0.00083,0.02771]}],"total_contact_groups":10},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64411,0.14725,0.17896],"final_tcp_position":[0.63654,0.14719,0.19408],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.63465,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":164.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":652.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53192,0.00083,0.18492],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15938,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":232.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":928.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.53818,0.001,0.03879],"tcp_start":[0.53192,0.00083,0.18492],"tcp_to_object_dist_end":0.01416,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54416,0.00071,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25054,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13022,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.16053,"subtask_id":"grasp_lift","tcp_end":[0.52885,0.00083,0.02767],"tcp_start":[0.53818,0.001,0.03879],"tcp_to_object_dist_end":0.01542,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":260.0,"n_steps_budget":1000.0,"object_pos_end":[0.53906,0.00062,0.14441],"object_pos_start":[0.54416,0.00071,0.02588],"object_to_goal_dist_end":0.19689,"object_to_goal_dist_start":0.25054,"object_z_max":0.14394,"peak_contact_force":0.08309,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10011.0,"raw_peak_contact_force":0.63465,"tcp_end":[0.52545,0.00077,0.14848],"tcp_start":[0.52885,0.00083,0.02767],"tcp_to_object_dist_end":0.0142,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":511.0,"n_steps_budget":1000.0,"object_pos_end":[0.64411,0.14725,0.17896],"object_pos_start":[0.53906,0.00062,0.14441],"object_to_goal_dist_end":0.01665,"object_to_goal_dist_start":0.19689,"object_z_max":0.17891,"peak_contact_force":0.07957,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":19286.0,"raw_peak_contact_force":0.13729,"subtask_id":"reach_goal","tcp_end":[0.63654,0.14719,0.19408],"tcp_start":[0.52545,0.00077,0.14848],"tcp_to_object_dist_end":0.01691,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```