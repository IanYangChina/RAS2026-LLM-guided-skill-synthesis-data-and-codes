## Search State

- **Seed**: 2
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.1604 | 0.38 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.1567 | 0.59 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.2445 | 0.77 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3874 | 0.96 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.4093 | 1.00 | ✅ accepted |

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

## Current Skill (Q=-0.160) — your mutation base

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

- **Composite score**: -0.160
- **task_score** (E): 0.380
- **fitness_score**: 0.670  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.830

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1497 |
| descend_1 | 1.00 | 1.00 | 0.1215 |
| grasp_1 | 1.00 | 1.00 | 0.0116 |
| lift_1 | 1.00 | 1.00 | 0.1645 |
| approach_2 | 1.00 | 0.67 | 0.2464 |
| descend_2 | 1.00 | 1.00 | 0.0880 |
| release_1 | 1.00 | 1.00 | 0.0201 |
| retract_1 | 1.00 | 1.00 | 0.1230 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.490, -0.014, 0.156) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.490, -0.014, 0.156)→(0.488, -0.015, 0.035) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.488, -0.015, 0.035)→(0.480, -0.015, 0.026) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 44.333 | 0.134 | 0.176 |
| lift_1 | lift | 1.00 / step_budget | (0.480, -0.015, 0.026)→(0.473, -0.015, 0.191) | (0.493, -0.015, 0.026)→(0.483, -0.015, 0.182) | 0.281→0.246 | 1.00 / 38.667 | 0.080 | 0.646 |
| approach_2 | approach | 1.00 / step_budget | (0.473, -0.015, 0.191)→(0.619, 0.158, 0.283) | (0.483, -0.015, 0.182)→(0.628, 0.167, 0.165) | 0.246→0.118 | 0.67 / 6.333 | 0.079 | 1.102 |
| descend_2 | descend | 1.00 / step_budget | (0.619, 0.158, 0.283)→(0.626, 0.169, 0.196) | (0.628, 0.167, 0.165)→(0.631, 0.177, 0.016) | 0.118→0.149 | 1.00 / 8.333 | 0.123 | 1.407 |
| release_1 | release | 1.00 / step_budget | (0.626, 0.169, 0.196)→(0.621, 0.167, 0.216) | (0.631, 0.177, 0.016)→(0.631, 0.177, 0.016) | 0.149→0.149 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_1 | retract | 1.00 / step_budget | (0.621, 0.167, 0.216)→(0.634, 0.174, 0.338) | (0.631, 0.177, 0.016)→(0.631, 0.177, 0.016) | 0.149→0.149 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.516
- phase_score: 0.385
- phase_breakdown.reach_pre_grasp_score: 0.439
- phase_breakdown.object_at_goal_score: 0.361
- grasp_place_fitness: 0.739

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.739
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.516
- **Median Q (composite search score)**: -0.193
- **K-run variance**: 0.0024
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.309


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44983,"average_solve_count":289.0,"average_success_count":289.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14979,"approach_2.arc_height":0.07977,"approach_2.transport_speed":0.14817,"descend_1.pre_grasp_tolerance":0.01607,"descend_2.descend_tolerance":0.0248,"descend_2.descent_speed":0.06829,"descend_2.placement_z_offset":0.02708,"grasp_1.grasp_time":0.42346,"lift_1.lift_distance":0.21948,"lift_1.lift_speed":0.03759,"release_1.release_time":0.58253,"retract_1.retract_height":0.17418,"retract_1.retract_speed":0.05602},"optimized_scores":{"best_composite_score":-0.19281,"best_fitness_score":0.63719,"best_task_score":0.31327},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1648.0,"contact_point_centroid":[0.63166,0.16535,-0.00293],"force_p95":0.36726,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.53619,"mean_force":0.16224,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.61592,0.14525,0.30722]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.47204,-0.01982,-0.00146],"force_p95":0.57529,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5992,"mean_force":0.26017,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46298,-0.01964,0.02808]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7737.0,"contact_point_centroid":[0.49319,-0.00323,0.28805],"force_p95":0.14626,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33391,"mean_force":0.0768,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49005,0.0155,0.28761]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7955.0,"contact_point_centroid":[0.49879,0.03916,0.29432],"force_p95":0.12836,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30626,"mean_force":0.0752,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49497,0.02051,0.29355]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20698.0,"contact_point_centroid":[0.45984,-0.00036,0.16271],"force_p95":0.07381,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26393,"mean_force":0.05214,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45968,-0.01953,0.16055]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":22037.0,"contact_point_centroid":[0.45973,-0.03863,0.16567],"force_p95":0.07209,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26367,"mean_force":0.04948,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45966,-0.01953,0.16376]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47615,-0.02003,-0.00204],"force_p95":0.13555,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17504,"mean_force":0.12622,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4651,-0.01969,0.02828]},{"body_a":"world","body_b":"grasp_target","contact_count":1336.0,"contact_point_centroid":[0.47616,-0.02015,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48756,-0.00843,0.2454]},{"body_a":"world","body_b":"grasp_target","contact_count":1968.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47255,-0.01867,0.11147]},{"body_a":"world","body_b":"grasp_target","contact_count":2288.0,"contact_point_centroid":[0.63167,0.16525,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62139,0.15277,0.23584]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.63167,0.16525,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61836,0.15301,0.22102]},{"body_a":"world","body_b":"grasp_target","contact_count":1888.0,"contact_point_centroid":[0.63167,0.16525,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.62211,0.1551,0.29178]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5068.0,"contact_point_centroid":[0.4637,-0.00042,0.02987],"force_p95":0.06575,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09225,"mean_force":0.04291,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46398,-0.01966,0.02719]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5396.0,"contact_point_centroid":[0.46357,-0.03891,0.02937],"force_p95":0.06457,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08731,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46399,-0.01966,0.02719]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1634.0,"contact_point_centroid":[0.61634,0.14526,0.30905],"force_p95":0.01162,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01635,"mean_force":0.01066,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.61586,0.14525,0.30671]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2454.0,"contact_point_centroid":[0.62203,0.1528,0.238],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.0104,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.6214,0.15278,0.23577]}],"total_contact_groups":17},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.63167,0.16525,0.01602],"final_tcp_position":[0.62869,0.158,0.34449],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":2.53619,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":335.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1336.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.47584,-0.0176,0.18943],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16343,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":492.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1968.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.4718,-0.01983,0.03494],"tcp_start":[0.47584,-0.0176,0.18943],"tcp_to_object_dist_end":0.00994,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01968,0.02584],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28826,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13378,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12264.0,"raw_peak_contact_force":0.17504,"tcp_end":[0.46396,-0.01966,0.02716],"tcp_start":[0.4718,-0.01983,0.03494],"tcp_to_object_dist_end":0.01215,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":668.0,"n_steps_budget":1000.0,"object_pos_end":[0.46641,-0.01935,0.21285],"object_pos_start":[0.47603,-0.01968,0.02584],"object_to_goal_dist_end":0.24419,"object_to_goal_dist_start":0.28826,"object_z_max":0.22152,"peak_contact_force":0.0716,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":42819.0,"raw_peak_contact_force":0.5992,"tcp_end":[0.45769,-0.01946,0.22206],"tcp_start":[0.46396,-0.01966,0.02716],"tcp_to_object_dist_end":0.01269,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":746.0,"n_steps_budget":1000.0,"object_pos_end":[0.63167,0.16525,0.01602],"object_pos_start":[0.46641,-0.01935,0.21285],"object_to_goal_dist_end":0.1741,"object_to_goal_dist_start":0.24419,"object_z_max":0.31763,"peak_contact_force":0.12263,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18974.0,"raw_peak_contact_force":2.53619,"tcp_end":[0.61572,0.14511,0.30613],"tcp_start":[0.45769,-0.01946,0.22206],"tcp_to_object_dist_end":0.29124,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":172.0,"n_steps_budget":1000.0,"object_pos_end":[0.63167,0.16525,0.01602],"object_pos_start":[0.63167,0.16525,0.01602],"object_to_goal_dist_end":0.1741,"object_to_goal_dist_start":0.1741,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4742.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62179,0.15405,0.22072],"tcp_start":[0.61572,0.14511,0.30613],"tcp_to_object_dist_end":0.20524,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63167,0.16525,0.01602],"object_pos_start":[0.63167,0.16525,0.01602],"object_to_goal_dist_end":0.1741,"object_to_goal_dist_start":0.1741,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"subtask_id":"object_at_goal","tcp_end":[0.61709,0.15258,0.24036],"tcp_start":[0.62179,0.15405,0.22072],"tcp_to_object_dist_end":0.22517,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":472.0,"n_steps_budget":1000.0,"object_pos_end":[0.63167,0.16525,0.01602],"object_pos_start":[0.63167,0.16525,0.01602],"object_to_goal_dist_end":0.1741,"object_to_goal_dist_start":0.1741,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1888.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62869,0.158,0.34449],"tcp_start":[0.61709,0.15258,0.24036],"tcp_to_object_dist_end":0.32857,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51553,"average_solve_count":322.0,"average_success_count":322.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.0814,"approach_2.arc_height":0.24401,"approach_2.transport_speed":0.04787,"descend_1.pre_grasp_tolerance":0.01334,"descend_2.descend_tolerance":0.01047,"descend_2.descent_speed":0.10643,"descend_2.placement_z_offset":0.02515,"grasp_1.grasp_time":0.5863,"lift_1.lift_distance":0.16718,"lift_1.lift_speed":0.04257,"release_1.release_time":0.48076,"retract_1.retract_height":0.19454,"retract_1.retract_speed":0.07302},"optimized_scores":{"best_composite_score":-0.09108,"best_fitness_score":0.73892,"best_task_score":0.51591},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2116.0,"contact_point_centroid":[0.61522,0.20537,-0.00261],"force_p95":0.18603,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.67542,"mean_force":0.14648,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61808,0.20012,0.15114]},{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.4544,-0.02537,-0.00143],"force_p95":0.58902,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60587,"mean_force":0.25137,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44578,-0.02556,0.02877]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18948.0,"contact_point_centroid":[0.5279,0.10121,0.25315],"force_p95":0.12513,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.49889,"mean_force":0.07101,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.52517,0.08245,0.25309]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19756.0,"contact_point_centroid":[0.52208,0.05684,0.25098],"force_p95":0.12534,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.49568,"mean_force":0.06821,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.51957,0.07557,0.2513]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18303.0,"contact_point_centroid":[0.44188,-0.04447,0.13594],"force_p95":0.07275,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27135,"mean_force":0.04931,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44192,-0.02537,0.13393]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16942.0,"contact_point_centroid":[0.44224,-0.0062,0.13334],"force_p95":0.07485,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26656,"mean_force":0.05254,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44208,-0.02538,0.13099]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02615,-0.00206],"force_p95":0.14072,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19366,"mean_force":0.12753,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44783,-0.02563,0.02872]},{"body_a":"world","body_b":"grasp_target","contact_count":2180.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47847,-0.01182,0.21068]},{"body_a":"world","body_b":"grasp_target","contact_count":1136.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45501,-0.02495,0.07779]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.61518,0.20533,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6136,0.19946,0.1414]},{"body_a":"world","body_b":"grasp_target","contact_count":2252.0,"contact_point_centroid":[0.61518,0.20533,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.61799,0.2023,0.2245]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4815.0,"contact_point_centroid":[0.44676,-0.00638,0.03007],"force_p95":0.06817,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09812,"mean_force":0.04487,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44674,-0.02559,0.02771]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5174.0,"contact_point_centroid":[0.44661,-0.04483,0.02957],"force_p95":0.06701,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08239,"mean_force":0.04301,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44675,-0.02559,0.02771]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2042.0,"contact_point_centroid":[0.61907,0.20084,0.14884],"force_p95":0.01137,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01647,"mean_force":0.01067,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61852,0.20081,0.14671]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.61697,0.20061,0.14073],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.01021,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61658,0.20056,0.13816]}],"total_contact_groups":15},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61518,0.20533,0.01602],"final_tcp_position":[0.62675,0.20662,0.28919],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.67542,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":546.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2180.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.45804,-0.02416,0.12114],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09515,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":284.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1136.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45431,-0.02586,0.03491],"tcp_start":[0.45804,-0.02416,0.12114],"tcp_to_object_dist_end":0.00986,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02563,0.02579],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30326,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13785,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11789.0,"raw_peak_contact_force":0.19366,"tcp_end":[0.44672,-0.02559,0.02768],"tcp_start":[0.45431,-0.02586,0.03491],"tcp_to_object_dist_end":0.01188,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":481.0,"n_steps_budget":1000.0,"object_pos_end":[0.44863,-0.02505,0.16239],"object_pos_start":[0.45844,-0.02563,0.02579],"object_to_goal_dist_end":0.29947,"object_to_goal_dist_start":0.30326,"object_z_max":0.17072,"peak_contact_force":0.07784,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":35327.0,"raw_peak_contact_force":0.60587,"tcp_end":[0.43979,-0.02527,0.17068],"tcp_start":[0.44672,-0.02559,0.02768],"tcp_to_object_dist_end":0.01212,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61438,0.19019,0.20658],"object_pos_start":[0.44863,-0.02505,0.16239],"object_to_goal_dist_end":0.09551,"object_to_goal_dist_start":0.29947,"object_z_max":0.27867,"peak_contact_force":0.0,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38704.0,"raw_peak_contact_force":0.49889,"tcp_end":[0.60806,0.18562,0.24322],"tcp_start":[0.43979,-0.02527,0.17068],"tcp_to_object_dist_end":0.03746,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":208.0,"n_steps_budget":1000.0,"object_pos_end":[0.61518,0.20533,0.01602],"object_pos_start":[0.61438,0.19019,0.20658],"object_to_goal_dist_end":0.09927,"object_to_goal_dist_start":0.09551,"object_z_max":0.20658,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4158.0,"raw_peak_contact_force":1.67542,"tcp_end":[0.61806,0.20107,0.14125],"tcp_start":[0.60806,0.18562,0.24322],"tcp_to_object_dist_end":0.12533,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61518,0.20533,0.01602],"object_pos_start":[0.61518,0.20533,0.01602],"object_to_goal_dist_end":0.09927,"object_to_goal_dist_start":0.09927,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"subtask_id":"object_at_goal","tcp_end":[0.61184,0.19879,0.16068],"tcp_start":[0.61806,0.20107,0.14125],"tcp_to_object_dist_end":0.14484,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.61518,0.20533,0.01602],"object_pos_start":[0.61518,0.20533,0.01602],"object_to_goal_dist_end":0.09927,"object_to_goal_dist_start":0.09927,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2252.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62675,0.20662,0.28919],"tcp_start":[0.61184,0.19879,0.16068],"tcp_to_object_dist_end":0.27342,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32534,"average_solve_count":292.0,"average_success_count":292.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12148,"approach_2.arc_height":0.19842,"approach_2.transport_speed":0.04865,"descend_1.pre_grasp_tolerance":0.01497,"descend_2.descend_tolerance":0.02591,"descend_2.descent_speed":0.05741,"descend_2.placement_z_offset":0.03285,"grasp_1.grasp_time":0.54747,"lift_1.lift_distance":0.18093,"lift_1.lift_speed":0.05704,"release_1.release_time":0.32386,"retract_1.retract_height":0.20834,"retract_1.retract_speed":0.08659},"optimized_scores":{"best_composite_score":-0.19734,"best_fitness_score":0.63266,"best_task_score":0.31115},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1777.0,"contact_point_centroid":[0.64504,0.16069,-0.00283],"force_p95":0.29675,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.4226,"mean_force":0.15487,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.63821,0.15207,0.22974]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.5409,0.00071,-0.00137],"force_p95":0.63303,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73259,"mean_force":0.19251,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52868,0.00084,0.02519]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17640.0,"contact_point_centroid":[0.52594,-0.0183,0.13705],"force_p95":0.08241,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3275,"mean_force":0.05728,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5248,0.00078,0.13497]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18255.0,"contact_point_centroid":[0.52585,0.01981,0.13548],"force_p95":0.07849,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3143,"mean_force":0.05549,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52478,0.00078,0.13364]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18902.0,"contact_point_centroid":[0.57339,0.04658,0.27779],"force_p95":0.12081,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27189,"mean_force":0.06676,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.57184,0.06556,0.27847]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20936.0,"contact_point_centroid":[0.57458,0.08625,0.27587],"force_p95":0.09103,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19907,"mean_force":0.05987,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.57333,0.06749,0.27675]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00098,-0.00203],"force_p95":0.13174,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16007,"mean_force":0.1253,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53114,0.00089,0.02548]},{"body_a":"world","body_b":"grasp_target","contact_count":1932.0,"contact_point_centroid":[0.54431,0.00113,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51711,0.00048,0.22843]},{"body_a":"world","body_b":"grasp_target","contact_count":1508.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53637,0.00099,0.09541]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.64502,0.16071,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63446,0.15105,0.22686]},{"body_a":"world","body_b":"grasp_target","contact_count":2264.0,"contact_point_centroid":[0.64502,0.16071,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.63867,0.15368,0.31206]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":59.0,"contact_point_centroid":[0.63527,0.15733,0.29461],"force_p95":0.09206,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11318,"mean_force":0.02398,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.63256,0.14249,0.30017]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53089,-0.01833,0.02675],"force_p95":0.07604,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11039,"mean_force":0.0517,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52988,0.00087,0.02405]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53083,0.01994,0.02587],"force_p95":0.06804,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09658,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52989,0.00087,0.02406]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1770.0,"contact_point_centroid":[0.63884,0.15222,0.23019],"force_p95":0.01154,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01736,"mean_force":0.01045,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.63814,0.15219,0.22812]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.637,0.15178,0.22614],"force_p95":0.01088,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0109,"mean_force":0.00993,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63669,0.15174,0.22391]}],"total_contact_groups":16},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64502,0.16071,0.01602],"final_tcp_position":[0.64608,0.15718,0.37954],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":2.4226,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":484.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1932.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.53682,0.00098,0.15785],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13204,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":377.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1508.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5386,0.00103,0.03413],"tcp_start":[0.53682,0.00098,0.15785],"tcp_to_object_dist_end":0.00992,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54415,0.00073,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12964,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.16007,"tcp_end":[0.52985,0.00086,0.02402],"tcp_start":[0.5386,0.00103,0.03413],"tcp_to_object_dist_end":0.01442,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":582.0,"n_steps_budget":1000.0,"object_pos_end":[0.53408,0.00051,0.16948],"object_pos_start":[0.54415,0.00073,0.02588],"object_to_goal_dist_end":0.19542,"object_to_goal_dist_start":0.25053,"object_z_max":0.18076,"peak_contact_force":0.09154,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":35981.0,"raw_peak_contact_force":0.73259,"tcp_end":[0.52247,0.00075,0.17916],"tcp_start":[0.52985,0.00086,0.02402],"tcp_to_object_dist_end":0.01512,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":891.0,"n_steps_budget":1000.0,"object_pos_end":[0.6382,0.14467,0.27379],"object_pos_start":[0.53408,0.00051,0.16948],"object_to_goal_dist_end":0.08429,"object_to_goal_dist_start":0.19542,"object_z_max":0.3037,"peak_contact_force":0.1139,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":39838.0,"raw_peak_contact_force":0.27189,"tcp_end":[0.63249,0.14244,0.30062],"tcp_start":[0.52247,0.00075,0.17916],"tcp_to_object_dist_end":0.02752,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":148.0,"n_steps_budget":1000.0,"object_pos_end":[0.64502,0.16071,0.01602],"object_pos_start":[0.6382,0.14467,0.27379],"object_to_goal_dist_end":0.17512,"object_to_goal_dist_start":0.08429,"object_z_max":0.27379,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3606.0,"raw_peak_contact_force":2.4226,"tcp_end":[0.63778,0.15205,0.22702],"tcp_start":[0.63249,0.14244,0.30062],"tcp_to_object_dist_end":0.21131,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.64502,0.16071,0.01602],"object_pos_start":[0.64502,0.16071,0.01602],"object_to_goal_dist_end":0.17512,"object_to_goal_dist_start":0.17512,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"subtask_id":"object_at_goal","tcp_end":[0.63324,0.15065,0.24598],"tcp_start":[0.63778,0.15205,0.22702],"tcp_to_object_dist_end":0.23048,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":566.0,"n_steps_budget":1000.0,"object_pos_end":[0.64502,0.16071,0.01602],"object_pos_start":[0.64502,0.16071,0.01602],"object_to_goal_dist_end":0.17512,"object_to_goal_dist_start":0.17512,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2264.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.64608,0.15718,0.37954],"tcp_start":[0.63324,0.15065,0.24598],"tcp_to_object_dist_end":0.36353,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```