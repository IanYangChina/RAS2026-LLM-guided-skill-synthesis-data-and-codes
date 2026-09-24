## Search State

- **Seed**: 2
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 11 | 0.3399 | 1.00 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 11 | 0.3400 | 1.00 | ✅ accepted |
| 12 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 11 | 0.3168 | 0.95 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 11 | 0.3112 | 0.94 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 12 | 0.2565 | 0.95 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (1.00). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.340) — your mutation base

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

- **Composite score**: 0.340
- **task_score** (E): 1.000
- **fitness_score**: 0.980  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.640

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1374 |
| descend_grasp | 1.00 | 1.00 | 0.1341 |
| grasp | 1.00 | 1.00 | 0.0114 |
| lift | 1.00 | 1.00 | 0.1241 |
| place_at_goal | 1.00 | 1.00 | 0.2368 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, -0.012, 0.168) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 21.728 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.493, -0.012, 0.168)→(0.488, -0.015, 0.034) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.488, -0.015, 0.034)→(0.480, -0.015, 0.026) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 44.667 | 0.134 | 0.176 |
| lift | lift | 1.00 / step_budget | (0.480, -0.015, 0.026)→(0.477, -0.015, 0.150) | (0.493, -0.015, 0.026)→(0.497, -0.015, 0.147) | 0.281→0.241 | 1.00 / 23.000 | 0.109 | 0.742 |
| place_at_goal | approach | 1.00 / step_budget | (0.477, -0.015, 0.150)→(0.624, 0.164, 0.172) | (0.497, -0.015, 0.147)→(0.632, 0.164, 0.154) | 0.241→0.018 | 1.00 / 30.000 | 0.104 | 0.246 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.056
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.642
- phase_breakdown.reach_goal_score: 0.645
- phase_breakdown.reach_object_score: 0.633
- grasp_place_fitness: 0.981

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.981
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.341
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.397


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.78571,"average_solve_count":84.0,"average_success_count":84.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.1308,"approach_object.speed":0.20375,"approach_object.tolerance":0.02176,"descend_grasp.descend_offset_z":0.00552,"descend_grasp.speed":0.22466,"lift.lift_height":0.14212,"lift.speed":0.15203,"lift.tolerance":0.02512,"place_at_goal.place_offset_z":0.01841,"place_at_goal.speed":0.22517,"place_at_goal.tolerance":0.04078},"optimized_scores":{"best_composite_score":0.34067,"best_fitness_score":0.98067,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":58.0,"contact_point_centroid":[0.47311,-0.01983,-0.00146],"force_p95":0.77667,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.79226,"mean_force":0.26535,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46252,-0.01962,0.02719]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3290.0,"contact_point_centroid":[0.46276,-0.00046,0.07637],"force_p95":0.1101,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35331,"mean_force":0.06779,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46112,-0.01957,0.0737]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3610.0,"contact_point_centroid":[0.46281,-0.0386,0.07542],"force_p95":0.10549,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34185,"mean_force":0.06296,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46111,-0.01957,0.07352]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7612.0,"contact_point_centroid":[0.54666,0.04968,0.1684],"force_p95":0.11809,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24987,"mean_force":0.08373,"phase_index":4.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.54267,0.0684,0.16726]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8209.0,"contact_point_centroid":[0.55001,0.08968,0.16951],"force_p95":0.1123,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21555,"mean_force":0.07803,"phase_index":4.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.54525,0.07114,0.16822]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47615,-0.02002,-0.00204],"force_p95":0.13558,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17546,"mean_force":0.12624,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46511,-0.01968,0.02718]},{"body_a":"world","body_b":"grasp_target","contact_count":596.0,"contact_point_centroid":[0.47616,-0.02015,-0.00179],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12345,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49052,-0.00715,0.24717]},{"body_a":"world","body_b":"grasp_target","contact_count":2760.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47436,-0.01752,0.10765]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5066.0,"contact_point_centroid":[0.46371,-0.00041,0.02877],"force_p95":0.06578,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09138,"mean_force":0.04291,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46399,-0.01965,0.02608]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5398.0,"contact_point_centroid":[0.46358,-0.03891,0.02826],"force_p95":0.06458,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08779,"mean_force":0.0412,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46399,-0.01965,0.02608]}],"total_contact_groups":10},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62866,0.14913,0.17501],"final_tcp_position":[0.61935,0.14907,0.19639],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.79226,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":150.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":596.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4802,-0.01514,0.18994],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":690.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2760.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.47167,-0.01982,0.03366],"tcp_start":[0.4802,-0.01514,0.18994],"tcp_to_object_dist_end":0.00887,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01966,0.02584],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28825,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13375,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12264.0,"raw_peak_contact_force":0.17546,"tcp_end":[0.46396,-0.01965,0.02605],"tcp_start":[0.47167,-0.01982,0.03366],"tcp_to_object_dist_end":0.01207,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":203.0,"n_steps_budget":600.0,"object_pos_end":[0.48124,-0.01943,0.13397],"object_pos_start":[0.47603,-0.01966,0.02584],"object_to_goal_dist_end":0.24,"object_to_goal_dist_start":0.28825,"object_z_max":0.13348,"peak_contact_force":0.10871,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6958.0,"raw_peak_contact_force":0.79226,"tcp_end":[0.46134,-0.01955,0.13832],"tcp_start":[0.46396,-0.01965,0.02605],"tcp_to_object_dist_end":0.02037,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":627.0,"n_steps_budget":1000.0,"object_pos_end":[0.62866,0.14913,0.17501],"object_pos_start":[0.48124,-0.01943,0.13397],"object_to_goal_dist_end":0.01828,"object_to_goal_dist_start":0.24,"object_z_max":0.17496,"peak_contact_force":0.11144,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15821.0,"raw_peak_contact_force":0.24987,"subtask_id":"reach_goal","tcp_end":[0.61935,0.14907,0.19639],"tcp_start":[0.46134,-0.01955,0.13832],"tcp_to_object_dist_end":0.02332,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.27778,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.11297,"approach_object.speed":0.14602,"approach_object.tolerance":0.02761,"descend_grasp.descend_offset_z":0.00583,"descend_grasp.speed":0.19003,"lift.lift_height":0.16661,"lift.speed":0.0854,"lift.tolerance":0.02358,"place_at_goal.place_offset_z":0.01909,"place_at_goal.speed":0.27652,"place_at_goal.tolerance":0.01695},"optimized_scores":{"best_composite_score":0.34136,"best_fitness_score":0.98136,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":62.0,"contact_point_centroid":[0.45647,-0.02525,-0.00149],"force_p95":0.63857,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64878,"mean_force":0.23029,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44584,-0.02556,0.02857]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4329.0,"contact_point_centroid":[0.44554,-0.00638,0.08866],"force_p95":0.10832,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28839,"mean_force":0.06541,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44403,-0.02546,0.08613]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4737.0,"contact_point_centroid":[0.44558,-0.04447,0.08798],"force_p95":0.10289,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2812,"mean_force":0.06105,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44401,-0.02546,0.08621]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9237.0,"contact_point_centroid":[0.54076,0.07707,0.14354],"force_p95":0.11352,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27715,"mean_force":0.07646,"phase_index":4.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.53835,0.09609,0.14224]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02614,-0.00206],"force_p95":0.14054,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19345,"mean_force":0.12752,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44805,-0.02564,0.0285]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11160.0,"contact_point_centroid":[0.54445,0.12029,0.14262],"force_p95":0.10157,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17333,"mean_force":0.05936,"phase_index":4.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.54275,0.10171,0.14127]},{"body_a":"world","body_b":"grasp_target","contact_count":716.0,"contact_point_centroid":[0.45856,-0.02632,-0.00182],"force_p95":0.1376,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12331,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48332,-0.00985,0.2377]},{"body_a":"world","body_b":"grasp_target","contact_count":2572.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.45826,-0.0233,0.0994]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4814.0,"contact_point_centroid":[0.44694,-0.00636,0.02974],"force_p95":0.06813,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09879,"mean_force":0.04493,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44696,-0.0256,0.02747]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5419.0,"contact_point_centroid":[0.44642,-0.04484,0.02914],"force_p95":0.06513,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08258,"mean_force":0.04118,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44697,-0.0256,0.02748]}],"total_contact_groups":10},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61692,0.19561,0.10931],"final_tcp_position":[0.61689,0.19533,0.12591],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":64.93862,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":180.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":64.93862,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":716.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.46536,-0.0207,0.17105],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1453,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":643.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2572.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45439,-0.02587,0.03452],"tcp_start":[0.46536,-0.0207,0.17105],"tcp_to_object_dist_end":0.00948,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02562,0.02579],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30324,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13748,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12033.0,"raw_peak_contact_force":0.19345,"tcp_end":[0.44694,-0.0256,0.02745],"tcp_start":[0.45439,-0.02587,0.03452],"tcp_to_object_dist_end":0.01163,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":264.0,"n_steps_budget":1000.0,"object_pos_end":[0.46376,-0.02533,0.16035],"object_pos_start":[0.45844,-0.02562,0.02579],"object_to_goal_dist_end":0.29044,"object_to_goal_dist_start":0.30324,"object_z_max":0.15986,"peak_contact_force":0.11045,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9128.0,"raw_peak_contact_force":0.64878,"tcp_end":[0.44406,-0.02543,0.16464],"tcp_start":[0.44694,-0.0256,0.02745],"tcp_to_object_dist_end":0.02016,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":655.0,"n_steps_budget":1000.0,"object_pos_end":[0.61692,0.19561,0.10931],"object_pos_start":[0.46376,-0.02533,0.16035],"object_to_goal_dist_end":0.01888,"object_to_goal_dist_start":0.29044,"object_z_max":0.16164,"peak_contact_force":0.08706,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20397.0,"raw_peak_contact_force":0.27715,"subtask_id":"reach_goal","tcp_end":[0.61689,0.19533,0.12591],"tcp_start":[0.44406,-0.02543,0.16464],"tcp_to_object_dist_end":0.01661,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.24752,"average_solve_count":101.0,"average_success_count":101.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_offset_z":0.08399,"approach_object.speed":0.26237,"approach_object.tolerance":0.01442,"descend_grasp.descend_offset_z":0.01027,"descend_grasp.speed":0.25685,"lift.lift_height":0.15205,"lift.speed":0.07624,"lift.tolerance":0.04881,"place_at_goal.place_offset_z":0.01451,"place_at_goal.speed":0.21986,"place_at_goal.tolerance":0.02592},"optimized_scores":{"best_composite_score":0.33766,"best_fitness_score":0.97766,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":68.0,"contact_point_centroid":[0.5409,0.00072,-0.00149],"force_p95":0.66708,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.78467,"mean_force":0.25892,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52905,0.00085,0.02447]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4177.0,"contact_point_centroid":[0.5285,-0.01826,0.08162],"force_p95":0.10345,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34411,"mean_force":0.06597,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52672,0.0008,0.07929]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4549.0,"contact_point_centroid":[0.52824,0.01978,0.07889],"force_p95":0.10403,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33015,"mean_force":0.06145,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52675,0.0008,0.07682]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6115.0,"contact_point_centroid":[0.58674,0.05852,0.16978],"force_p95":0.11932,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21026,"mean_force":0.08533,"phase_index":4.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.58293,0.07723,0.16883]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6689.0,"contact_point_centroid":[0.5896,0.09832,0.17079],"force_p95":0.11109,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20371,"mean_force":0.07909,"phase_index":4.0,"phase_name":"place_at_goal","phase_type":"approach","tcp_position_centroid":[0.58487,0.07981,0.16967]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00099,-0.00203],"force_p95":0.13159,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15948,"mean_force":0.12529,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53162,0.0009,0.02497]},{"body_a":"world","body_b":"grasp_target","contact_count":848.0,"contact_point_centroid":[0.54431,0.00113,-0.00185],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1232,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51609,0.00043,0.22267]},{"body_a":"world","body_b":"grasp_target","contact_count":3728.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53498,0.00094,0.07794]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53119,-0.01832,0.02623],"force_p95":0.07602,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10981,"mean_force":0.05171,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53035,0.00088,0.02351]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53115,0.01995,0.02534],"force_p95":0.068,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09637,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53035,0.00088,0.02352]}],"total_contact_groups":10},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64903,0.14741,0.17649],"final_tcp_position":[0.63675,0.14739,0.19303],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.78467,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":213.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":848.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53364,0.00088,0.14185],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11632,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":932.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3728.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53881,0.00103,0.03327],"tcp_start":[0.53364,0.00088,0.14185],"tcp_to_object_dist_end":0.0091,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54415,0.00074,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12951,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15948,"tcp_end":[0.53032,0.00087,0.02348],"tcp_start":[0.53881,0.00103,0.03327],"tcp_to_object_dist_end":0.01404,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":255.0,"n_steps_budget":1000.0,"object_pos_end":[0.54595,0.00087,0.14583],"object_pos_start":[0.54415,0.00074,0.02588],"object_to_goal_dist_end":0.19263,"object_to_goal_dist_start":0.25053,"object_z_max":0.14538,"peak_contact_force":0.10858,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8794.0,"raw_peak_contact_force":0.78467,"tcp_end":[0.52659,0.00081,0.1462],"tcp_start":[0.53032,0.00087,0.02348],"tcp_to_object_dist_end":0.01936,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":513.0,"n_steps_budget":1000.0,"object_pos_end":[0.64903,0.14741,0.17649],"object_pos_start":[0.54595,0.00087,0.14583],"object_to_goal_dist_end":0.01815,"object_to_goal_dist_start":0.19263,"object_z_max":0.17645,"peak_contact_force":0.114,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12804.0,"raw_peak_contact_force":0.21026,"subtask_id":"reach_goal","tcp_end":[0.63675,0.14739,0.19303],"tcp_start":[0.52659,0.00081,0.1462],"tcp_to_object_dist_end":0.0206,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```