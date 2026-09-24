## Search State

- **Seed**: 2
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3874 | 0.96 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.4093 | 1.00 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.4259 | 0.93 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | 0.0955 | 0.39 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | -0.1265 | 0.15 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.96). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.387) — your mutation base

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
  - 0.05
  weight: 0.3
- id: object_at_goal
  target_entity: object
  weight: 0.7
phases:
- id: approach_1
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
    - 0.05
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_pre_grasp
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
    pre_grasp_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
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
    grasp_time:
      type: scalar
      range:
      - 0.2
      - 1.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  end_effector_action: force_grasp
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_distance:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: object_lifted_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.03
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.03
- id: approach_2
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    descent_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    placement_z_offset:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: object_at_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - pre_grasp_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_time: status=consumed; consumers=duration.max_time (replace)
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=object_lifted_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.03
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.03]
- **approach_2** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - descent_speed: status=consumed; consumers=generator.speed (replace)
    - placement_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.387
- **task_score** (E): 0.956
- **fitness_score**: 0.957  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1580 |
| descend_1 | 1.00 | 1.00 | 0.1130 |
| grasp_1 | 1.00 | 1.00 | 0.0116 |
| lift_1 | 1.00 | 1.00 | 0.1152 |
| approach_2 | 0.00 | 1.00 | 0.1083 |
| descend_2 | 1.00 | 1.00 | 0.1382 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.490, -0.014, 0.148) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.490, -0.014, 0.148)→(0.488, -0.015, 0.035) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.488, -0.015, 0.035)→(0.480, -0.015, 0.026) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 44.333 | 0.134 | 0.176 |
| lift_1 | lift | 1.00 / step_budget | (0.480, -0.015, 0.026)→(0.472, -0.015, 0.141) | (0.493, -0.015, 0.026)→(0.483, -0.015, 0.134) | 0.281→0.253 | 1.00 / 41.333 | 0.074 | 0.531 |
| approach_2 | approach | 0.00 / step_budget | (0.472, -0.015, 0.141)→(0.534, 0.063, 0.177) | (0.483, -0.015, 0.134)→(0.539, 0.063, 0.159) | 0.253→0.154 | 1.00 / 36.667 | 0.078 | 0.115 |
| descend_2 | descend | 1.00 / step_budget | (0.534, 0.063, 0.177)→(0.621, 0.164, 0.186) | (0.539, 0.063, 0.159)→(0.624, 0.163, 0.160) | 0.154→0.019 | 1.00 / 25.000 | 0.115 | 0.238 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.220
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.384
- phase_breakdown.reach_pre_grasp_score: 0.194
- phase_breakdown.object_at_goal_score: 0.466
- grasp_place_fitness: 0.980

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.980
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.407
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.348


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.14545,"average_solve_count":220.0,"average_success_count":220.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12228,"approach_2.transport_speed":0.18794,"descend_1.pre_grasp_tolerance":0.0107,"descend_2.descend_tolerance":0.03392,"descend_2.descent_speed":0.14531,"descend_2.placement_z_offset":0.05402,"grasp_1.grasp_time":0.99967,"lift_1.lift_distance":0.13731,"lift_1.lift_speed":0.01164},"optimized_scores":{"best_composite_score":0.41048,"best_fitness_score":0.98048,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":104.0,"contact_point_centroid":[0.47254,-0.01981,-0.00152],"force_p95":0.44893,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51858,"mean_force":0.24445,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46278,-0.01964,0.02781]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8494.0,"contact_point_centroid":[0.60096,0.11093,0.21957],"force_p95":0.12272,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29852,"mean_force":0.08007,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59764,0.1296,0.22126]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8887.0,"contact_point_centroid":[0.59923,0.14638,0.21932],"force_p95":0.12345,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26261,"mean_force":0.07762,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.5958,0.12777,0.22078]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16866.0,"contact_point_centroid":[0.4586,-0.03861,0.11481],"force_p95":0.073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23117,"mean_force":0.04942,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45862,-0.01951,0.1128]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15712.0,"contact_point_centroid":[0.45892,-0.00034,0.11313],"force_p95":0.07487,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23036,"mean_force":0.05239,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45878,-0.01951,0.11084]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47615,-0.02002,-0.00204],"force_p95":0.13519,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17485,"mean_force":0.12613,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46504,-0.01969,0.0282]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21326.0,"contact_point_centroid":[0.51165,0.02078,0.18463],"force_p95":0.09282,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16156,"mean_force":0.06356,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51076,0.03993,0.18328]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":27058.0,"contact_point_centroid":[0.51181,0.05882,0.18415],"force_p95":0.07625,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14964,"mean_force":0.05106,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51077,0.03996,0.18326]},{"body_a":"world","body_b":"grasp_target","contact_count":1660.0,"contact_point_centroid":[0.47616,-0.02015,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48701,-0.00873,0.23152]},{"body_a":"world","body_b":"grasp_target","contact_count":1632.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47212,-0.01889,0.09787]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5067.0,"contact_point_centroid":[0.46366,-0.00042,0.02984],"force_p95":0.06584,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09138,"mean_force":0.04291,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46393,-0.01966,0.0271]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5396.0,"contact_point_centroid":[0.46353,-0.03892,0.02933],"force_p95":0.06454,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08718,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46393,-0.01966,0.0271]}],"total_contact_groups":12},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62016,0.14856,0.18812],"final_tcp_position":[0.61918,0.1493,0.23191],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.51858,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":416.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1660.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.47507,-0.01804,0.16199],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13599,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":408.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1632.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47173,-0.01984,0.03485],"tcp_start":[0.47507,-0.01804,0.16199],"tcp_to_object_dist_end":0.00989,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01968,0.02585],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28826,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13346,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12263.0,"raw_peak_contact_force":0.17485,"tcp_end":[0.4639,-0.01966,0.02707],"tcp_start":[0.47173,-0.01984,0.03485],"tcp_to_object_dist_end":0.0122,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":413.0,"n_steps_budget":1000.0,"object_pos_end":[0.46582,-0.01933,0.13321],"object_pos_start":[0.47603,-0.01968,0.02585],"object_to_goal_dist_end":0.25004,"object_to_goal_dist_start":0.28826,"object_z_max":0.14184,"peak_contact_force":0.07192,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32682.0,"raw_peak_contact_force":0.51858,"tcp_end":[0.45638,-0.01943,0.1402],"tcp_start":[0.4639,-0.01966,0.02707],"tcp_to_object_dist_end":0.01175,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54876,0.07638,0.18628],"object_pos_start":[0.46582,-0.01933,0.13321],"object_to_goal_dist_end":0.11707,"object_to_goal_dist_start":0.25004,"object_z_max":0.19555,"peak_contact_force":0.0955,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":48384.0,"raw_peak_contact_force":0.16156,"tcp_end":[0.54426,0.07635,0.20798],"tcp_start":[0.45638,-0.01943,0.1402],"tcp_to_object_dist_end":0.02216,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":324.0,"n_steps_budget":1000.0,"object_pos_end":[0.62016,0.14856,0.18812],"object_pos_start":[0.54876,0.07638,0.18628],"object_to_goal_dist_end":0.0156,"object_to_goal_dist_start":0.11707,"object_z_max":0.20104,"peak_contact_force":0.11461,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":17381.0,"raw_peak_contact_force":0.29852,"subtask_id":"object_at_goal","tcp_end":[0.61588,0.14837,0.22316],"tcp_start":[0.54426,0.07635,0.20798],"tcp_to_object_dist_end":0.0353,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.06269,"average_solve_count":335.0,"average_success_count":335.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08347,"approach_2.transport_speed":0.08208,"descend_1.pre_grasp_tolerance":0.0086,"descend_2.descend_tolerance":0.02548,"descend_2.descent_speed":0.01584,"descend_2.placement_z_offset":0.03327,"grasp_1.grasp_time":0.76203,"lift_1.lift_distance":0.16232,"lift_1.lift_speed":0.02576},"optimized_scores":{"best_composite_score":0.34476,"best_fitness_score":0.91476,"best_task_score":0.86771},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":94.0,"contact_point_centroid":[0.45476,-0.02543,-0.00153],"force_p95":0.50298,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53096,"mean_force":0.25402,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44568,-0.02556,0.02862]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18271.0,"contact_point_centroid":[0.44184,-0.04447,0.13201],"force_p95":0.07271,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2361,"mean_force":0.04939,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44185,-0.02537,0.12998]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17063.0,"contact_point_centroid":[0.44216,-0.00621,0.12979],"force_p95":0.07476,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23065,"mean_force":0.05219,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.442,-0.02538,0.12746]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15754.0,"contact_point_centroid":[0.58856,0.18226,0.14592],"force_p95":0.08899,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22398,"mean_force":0.05623,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58715,0.16311,0.14473]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02615,-0.00206],"force_p95":0.14074,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19361,"mean_force":0.12753,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44781,-0.02563,0.02886]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18404.0,"contact_point_centroid":[0.58535,0.14116,0.14664],"force_p95":0.07265,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18634,"mean_force":0.04814,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58467,0.16006,0.1459]},{"body_a":"world","body_b":"grasp_target","contact_count":2148.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13215,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47845,-0.01183,0.21148]},{"body_a":"world","body_b":"grasp_target","contact_count":1152.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45501,-0.02495,0.07885]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4815.0,"contact_point_centroid":[0.44675,-0.00638,0.03022],"force_p95":0.06818,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09815,"mean_force":0.04488,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44673,-0.02559,0.02785]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":28706.0,"contact_point_centroid":[0.48957,0.02164,0.17472],"force_p95":0.06821,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09027,"mean_force":0.04759,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.48937,0.04076,0.17296]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5174.0,"contact_point_centroid":[0.4466,-0.04483,0.02971],"force_p95":0.06702,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08228,"mean_force":0.04301,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44673,-0.02559,0.02785]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":27741.0,"contact_point_centroid":[0.48942,0.05955,0.17473],"force_p95":0.07016,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07875,"mean_force":0.04916,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.48904,0.0404,0.17285]}],"total_contact_groups":12},"final_pose_error":0.01975,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61453,0.19381,0.11257],"final_tcp_position":[0.61645,0.19549,0.141],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.53096,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":538.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2148.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.45805,-0.02415,0.12307],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09707,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":288.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1152.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45432,-0.02586,0.03506],"tcp_start":[0.45805,-0.02415,0.12307],"tcp_to_object_dist_end":0.01,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02564,0.02579],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30326,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13786,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11789.0,"raw_peak_contact_force":0.19361,"tcp_end":[0.4467,-0.02559,0.02782],"tcp_start":[0.45432,-0.02586,0.03506],"tcp_to_object_dist_end":0.01192,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":483.0,"n_steps_budget":1000.0,"object_pos_end":[0.44849,-0.02505,0.15803],"object_pos_start":[0.45844,-0.02564,0.02579],"object_to_goal_dist_end":0.29888,"object_to_goal_dist_start":0.30326,"object_z_max":0.16626,"peak_contact_force":0.0778,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":35428.0,"raw_peak_contact_force":0.53096,"tcp_end":[0.43969,-0.02527,0.16605],"tcp_start":[0.4467,-0.02559,0.02782],"tcp_to_object_dist_end":0.01191,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51687,0.07307,0.15873],"object_pos_start":[0.44849,-0.02505,0.15803],"object_to_goal_dist_end":0.18188,"object_to_goal_dist_start":0.29888,"object_z_max":0.16661,"peak_contact_force":0.06721,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":56447.0,"raw_peak_contact_force":0.09027,"tcp_end":[0.51313,0.07307,0.17447],"tcp_start":[0.43969,-0.02527,0.16605],"tcp_to_object_dist_end":0.01618,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":504.0,"n_steps_budget":1000.0,"object_pos_end":[0.61453,0.19381,0.11257],"object_pos_start":[0.51687,0.07307,0.15873],"object_to_goal_dist_end":0.02129,"object_to_goal_dist_start":0.18188,"object_z_max":0.15873,"peak_contact_force":0.07192,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":34158.0,"raw_peak_contact_force":0.22398,"subtask_id":"object_at_goal","tcp_end":[0.61207,0.19401,0.13212],"tcp_start":[0.51313,0.07307,0.17447],"tcp_to_object_dist_end":0.0197,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96337,"average_solve_count":273.0,"average_success_count":273.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12152,"approach_2.transport_speed":0.04739,"descend_1.pre_grasp_tolerance":0.01152,"descend_2.descend_tolerance":0.02122,"descend_2.descent_speed":0.04569,"descend_2.placement_z_offset":0.03431,"grasp_1.grasp_time":0.60231,"lift_1.lift_distance":0.11871,"lift_1.lift_speed":0.02333},"optimized_scores":{"best_composite_score":0.40709,"best_fitness_score":0.97709,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":112.0,"contact_point_centroid":[0.54004,0.00072,-0.00154],"force_p95":0.47603,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54286,"mean_force":0.2368,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52854,0.00083,0.02469]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14669.0,"contact_point_centroid":[0.52451,-0.01834,0.09749],"force_p95":0.07828,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24219,"mean_force":0.05495,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52387,0.00076,0.09513]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15153.0,"contact_point_centroid":[0.52452,0.01984,0.09579],"force_p95":0.07726,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23834,"mean_force":0.05372,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52394,0.00076,0.09365]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12225.0,"contact_point_centroid":[0.60879,0.13329,0.18599],"force_p95":0.12877,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19275,"mean_force":0.07691,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60619,0.11431,0.18685]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16400.0,"contact_point_centroid":[0.6062,0.09419,0.18499],"force_p95":0.08469,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17267,"mean_force":0.05679,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60489,0.11279,0.18599]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00098,-0.00203],"force_p95":0.13174,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16007,"mean_force":0.1253,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53114,0.00089,0.02549]},{"body_a":"world","body_b":"grasp_target","contact_count":1932.0,"contact_point_centroid":[0.54431,0.00113,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51711,0.00048,0.22845]},{"body_a":"world","body_b":"grasp_target","contact_count":1508.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53638,0.00099,0.09543]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53089,-0.01833,0.02675],"force_p95":0.07604,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11039,"mean_force":0.0517,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52988,0.00087,0.02406]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53083,0.01994,0.02587],"force_p95":0.06804,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09657,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52989,0.00087,0.02406]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":28688.0,"contact_point_centroid":[0.53824,0.00796,0.14007],"force_p95":0.07162,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09409,"mean_force":0.0486,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.53771,0.02708,0.1392]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":28157.0,"contact_point_centroid":[0.53868,0.04669,0.1405],"force_p95":0.07126,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08515,"mean_force":0.04938,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.53804,0.02755,0.13964]}],"total_contact_groups":12},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.63743,0.14782,0.17906],"final_tcp_position":[0.63745,0.14912,0.211],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.54286,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":484.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1932.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.53682,0.00098,0.15789],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13208,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":377.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1508.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5386,0.00103,0.03414],"tcp_start":[0.53682,0.00098,0.15789],"tcp_to_object_dist_end":0.00993,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54415,0.00073,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12964,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.16007,"tcp_end":[0.52985,0.00086,0.02402],"tcp_start":[0.5386,0.00103,0.03414],"tcp_to_object_dist_end":0.01442,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":386.0,"n_steps_budget":1000.0,"object_pos_end":[0.53337,0.00075,0.11164],"object_pos_start":[0.54415,0.00073,0.02588],"object_to_goal_dist_end":0.21005,"object_to_goal_dist_start":0.25053,"object_z_max":0.12253,"peak_contact_force":0.07148,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29934.0,"raw_peak_contact_force":0.54286,"tcp_end":[0.52133,0.00073,0.11744],"tcp_start":[0.52985,0.00086,0.02402],"tcp_to_object_dist_end":0.01336,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55094,0.03995,0.13221],"object_pos_start":[0.53337,0.00075,0.11164],"object_to_goal_dist_end":0.16362,"object_to_goal_dist_start":0.21005,"object_z_max":0.14116,"peak_contact_force":0.07184,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":56845.0,"raw_peak_contact_force":0.09409,"tcp_end":[0.54505,0.03997,0.14827],"tcp_start":[0.52133,0.00073,0.11744],"tcp_to_object_dist_end":0.0171,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":599.0,"n_steps_budget":1000.0,"object_pos_end":[0.63743,0.14782,0.17906],"object_pos_start":[0.55094,0.03995,0.13221],"object_to_goal_dist_end":0.01882,"object_to_goal_dist_start":0.16362,"object_z_max":0.19186,"peak_contact_force":0.15725,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":28625.0,"raw_peak_contact_force":0.19275,"subtask_id":"object_at_goal","tcp_end":[0.63389,0.14815,0.20179],"tcp_start":[0.54505,0.03997,0.14827],"tcp_to_object_dist_end":0.02301,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```