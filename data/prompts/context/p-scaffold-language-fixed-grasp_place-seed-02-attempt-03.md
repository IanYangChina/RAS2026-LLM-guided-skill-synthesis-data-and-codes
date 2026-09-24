## Search State

- **Seed**: 2
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 11 | -0.1049 | 0.20 | ✅ accepted |
| 2 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | position_control | admittance_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | 3 | 0.3009 | 0.16 | ✅ accepted |
| 1 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | position_control | admittance_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | 3 | 0.3009 | 0.15 | ✅ accepted |
| 0 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | position_control | admittance_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | 3 | 0.3008 | 0.15 | ✅ accepted |

**Proposal policy**: task_score is 0.20 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach_1 | object | (0.00, 0.00, 0.00) | distance | approach_height |
| descend_1 | object | (0.00, 0.00, 0.02) | distance | grasp_z_offset |
| grasp_1 | object | (0.00, 0.00, 0.02) | contact | — |
| transport_arc | goal | (0.00, 0.00, 0.00) | distance | — |
| release_1 | goal | (0.00, 0.00, 0.00) | distance | — |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=-0.105) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: add
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - -0.01
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: add
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: descend_1
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
  parameters:
    grip_force:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 20.0
      binds_to:
      - path: guards.grip_force_guard.threshold
        mode: replace
  guards:
  - id: grip_force_guard
    when: during_phase
    predicate: force_below
    threshold: 20.0
    on_failure: abort
  subtask_id: grasp_1
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
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.02
    orientation:
      mode: keep_current
  parameters:
    duration:
      type: scalar
      range:
      - 0.2
      - 1.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (add)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (add)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grip_force: status=consumed; consumers=guards.grip_force_guard.threshold (replace)
  - guards:
    - id=grip_force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=20.0
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02]
  - orientation: mode=keep_current
  - parameter_bindings:
    - duration: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: -0.105
- **task_score** (E): 0.196
- **fitness_score**: 0.565  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.670

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1445 |
| descend_1 | 1.00 | 1.00 | 0.1111 |
| grasp_1 | 1.00 | 1.00 | 0.0111 |
| lift_1 | 0.67 | 1.00 | 0.1080 |
| transport_1 | 0.00 | 1.00 | 0.1066 |
| release_1 | 1.00 | 1.00 | 0.0245 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.491, -0.013, 0.162) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.491, -0.013, 0.162)→(0.488, -0.015, 0.051) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.488, -0.015, 0.051)→(0.480, -0.015, 0.043) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 45.000 | 0.134 | 0.167 |
| lift_1 | lift | 0.67 / step_budget | (0.480, -0.015, 0.043)→(0.487, -0.015, 0.150) | (0.493, -0.015, 0.026)→(0.498, -0.015, 0.126) | 0.281→0.244 | 1.00 / 26.333 | 80.072 | 0.386 |
| transport_1 | approach | 0.00 / step_budget | (0.487, -0.015, 0.150)→(0.524, 0.036, 0.226) | (0.498, -0.015, 0.126)→(0.532, 0.015, 0.016) | 0.244→0.245 | 1.00 / 4.000 | 0.118 | 1.519 |
| release_1 | release | 1.00 / step_budget | (0.524, 0.036, 0.226)→(0.519, 0.035, 0.250) | (0.532, 0.015, 0.016)→(0.532, 0.015, 0.016) | 0.245→0.245 | 1.00 / 4.000 | 0.123 | 0.126 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.230
- phase_score: 0.254
- phase_breakdown.transport_arc_score: 0.016
- phase_breakdown.approach_1_score: 0.045
- phase_breakdown.descend_1_score: 0.910
- phase_breakdown.release_1_score: 0.012
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.581

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.581
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.230
- **Median Q (composite search score)**: -0.108
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.366


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21547,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13195,"approach_1.speed":0.06513,"descend_1.grasp_z_offset":-0.00617,"descend_1.speed":0.03614,"grasp_1.grip_force":14.38114,"lift_1.lift_height":0.1746,"lift_1.speed":0.05705,"release_1.duration":0.40187,"transport_1.arc_height":0.05142,"transport_1.transport_height":0.12329,"transport_1.transport_speed":0.096},"optimized_scores":{"best_composite_score":-0.10805,"best_fitness_score":0.56195,"best_task_score":0.17036},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":274.0,"contact_point_centroid":[0.5068,0.00166,-0.00621],"force_p95":1.11616,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.56845,"mean_force":0.30394,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49876,0.01824,0.21985]},{"body_a":"world","body_b":"grasp_target","contact_count":164.0,"contact_point_centroid":[0.47259,-0.01945,-0.00117],"force_p95":0.28134,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47832,"mean_force":0.06894,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46286,-0.0197,0.03598]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19053.0,"contact_point_centroid":[0.46419,-0.00016,0.08264],"force_p95":0.0584,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26782,"mean_force":0.03352,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46375,-0.01964,0.0807]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19038.0,"contact_point_centroid":[0.4642,-0.03914,0.08203],"force_p95":0.0588,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26218,"mean_force":0.03389,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46373,-0.01964,0.08024]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8704.0,"contact_point_centroid":[0.47955,0.01196,0.16429],"force_p95":0.09714,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18376,"mean_force":0.05541,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.47511,-0.00727,0.16493]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9659.0,"contact_point_centroid":[0.47967,-0.02628,0.16428],"force_p95":0.08821,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18063,"mean_force":0.0508,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.47524,-0.00714,0.16516]},{"body_a":"world","body_b":"grasp_target","contact_count":1616.0,"contact_point_centroid":[0.47616,-0.02009,-0.00203],"force_p95":0.13391,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17115,"mean_force":0.1255,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46543,-0.01977,0.03564]},{"body_a":"world","body_b":"grasp_target","contact_count":1624.0,"contact_point_centroid":[0.47616,-0.02015,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48702,-0.00864,0.23622]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50703,0.00194,-0.00194],"force_p95":0.12877,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13061,"mean_force":0.12168,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49695,0.01975,0.22625]},{"body_a":"world","body_b":"grasp_target","contact_count":3264.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47186,-0.01888,0.1036]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.46372,-0.00022,0.03732],"force_p95":0.04801,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09007,"mean_force":0.02445,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46422,-0.01974,0.03443]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4370.0,"contact_point_centroid":[0.46363,-0.03927,0.03675],"force_p95":0.04789,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08111,"mean_force":0.0237,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46422,-0.01974,0.03443]}],"total_contact_groups":12},"final_pose_error":0.21182,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.50703,0.00194,0.01602],"final_tcp_position":[0.5003,0.01987,0.22239],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.56845,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":407.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1624.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47533,-0.0179,0.17165],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14566,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":816.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3264.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47166,-0.01992,0.04191],"tcp_start":[0.47533,-0.0179,0.17165],"tcp_to_object_dist_end":0.01652,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47605,-0.0198,0.02585],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28832,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13306,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10101.0,"raw_peak_contact_force":0.17115,"subtask_id":"grasp_1","tcp_end":[0.46418,-0.01974,0.0344],"tcp_start":[0.47166,-0.01992,0.04191],"tcp_to_object_dist_end":0.01463,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47841,-0.01964,0.11244],"object_pos_start":[0.47605,-0.0198,0.02585],"object_to_goal_dist_end":0.24781,"object_to_goal_dist_start":0.28832,"object_z_max":0.11236,"peak_contact_force":0.06369,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38255.0,"raw_peak_contact_force":0.47832,"tcp_end":[0.46722,-0.01965,0.12879],"tcp_start":[0.46418,-0.01974,0.0344],"tcp_to_object_dist_end":0.01981,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50701,0.00252,0.01656],"object_pos_start":[0.47841,-0.01964,0.11244],"object_to_goal_dist_end":0.26479,"object_to_goal_dist_start":0.24781,"object_z_max":0.18346,"peak_contact_force":0.10884,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18637.0,"raw_peak_contact_force":1.56845,"subtask_id":"transport_arc","tcp_end":[0.5003,0.01987,0.22239],"tcp_start":[0.46722,-0.01965,0.12879],"tcp_to_object_dist_end":0.20667,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50703,0.00194,0.01602],"object_pos_start":[0.50701,0.00252,0.01656],"object_to_goal_dist_end":0.26548,"object_to_goal_dist_start":0.26479,"object_z_max":0.01679,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":800.0,"raw_peak_contact_force":0.13061,"subtask_id":"release_1","tcp_end":[0.49568,0.01969,0.24721],"tcp_start":[0.5003,0.01987,0.22239],"tcp_to_object_dist_end":0.23215,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.02804,"average_solve_count":214.0,"average_success_count":214.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14624,"approach_1.speed":0.08436,"descend_1.grasp_z_offset":0.00347,"descend_1.speed":0.02093,"grasp_1.grip_force":16.97703,"lift_1.lift_height":0.1572,"lift_1.speed":0.09993,"release_1.duration":0.5697,"transport_1.arc_height":0.037,"transport_1.transport_height":0.08747,"transport_1.transport_speed":0.08033},"optimized_scores":{"best_composite_score":-0.08944,"best_fitness_score":0.58056,"best_task_score":0.23035},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":584.0,"contact_point_centroid":[0.52853,0.03863,-0.0038],"force_p95":0.82019,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.70739,"mean_force":0.20278,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51409,0.05787,0.21131]},{"body_a":"world","body_b":"grasp_target","contact_count":124.0,"contact_point_centroid":[0.45657,-0.02515,-0.00111],"force_p95":0.26197,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3684,"mean_force":0.03745,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44616,-0.02567,0.04691]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13188.0,"contact_point_centroid":[0.4508,-0.04504,0.10208],"force_p95":0.06799,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24821,"mean_force":0.03963,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44841,-0.02564,0.10042]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12159.0,"contact_point_centroid":[0.45095,-0.00621,0.10274],"force_p95":0.07055,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24537,"mean_force":0.04181,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44846,-0.02564,0.10128]},{"body_a":"world","body_b":"grasp_target","contact_count":1616.0,"contact_point_centroid":[0.45857,-0.02628,-0.00204],"force_p95":0.13789,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17732,"mean_force":0.12651,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44841,-0.02576,0.04625]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6601.0,"contact_point_centroid":[0.4798,0.02319,0.18618],"force_p95":0.09716,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15652,"mean_force":0.06198,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.47361,0.00405,0.1874]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7632.0,"contact_point_centroid":[0.4811,-0.01306,0.1868],"force_p95":0.08244,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15021,"mean_force":0.05473,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.47503,0.00594,0.18846]},{"body_a":"world","body_b":"grasp_target","contact_count":1456.0,"contact_point_centroid":[0.45856,-0.02632,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47981,-0.01119,0.24307]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52903,0.03894,-0.00199],"force_p95":0.12283,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12326,"mean_force":0.12262,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51551,0.06406,0.21638]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3902.0,"contact_point_centroid":[0.44637,-0.00621,0.04731],"force_p95":0.04949,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12291,"mean_force":0.02586,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44725,-0.02572,0.04512]},{"body_a":"world","body_b":"grasp_target","contact_count":3544.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45561,-0.02457,0.11584]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4379.0,"contact_point_centroid":[0.44682,-0.04523,0.0478],"force_p95":0.04885,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08047,"mean_force":0.02359,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44725,-0.02572,0.04513]}],"total_contact_groups":12},"final_pose_error":0.18207,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.52903,0.03894,0.01602],"final_tcp_position":[0.51902,0.06442,0.213],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":240.09112,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":365.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1456.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.46007,-0.02324,0.18537],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15938,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":886.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3544.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45436,-0.02599,0.0521],"tcp_start":[0.46007,-0.02324,0.18537],"tcp_to_object_dist_end":0.02642,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45849,-0.0259,0.02579],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30343,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13703,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9897.0,"raw_peak_contact_force":0.17732,"subtask_id":"grasp_1","tcp_end":[0.44721,-0.02572,0.04509],"tcp_start":[0.45436,-0.02599,0.0521],"tcp_to_object_dist_end":0.02235,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.46645,-0.02595,0.14539],"object_pos_start":[0.45849,-0.0259,0.02579],"object_to_goal_dist_end":0.28741,"object_to_goal_dist_start":0.30343,"object_z_max":0.14528,"peak_contact_force":240.09112,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25471.0,"raw_peak_contact_force":0.3684,"tcp_end":[0.45441,-0.02573,0.17171],"tcp_start":[0.44721,-0.02572,0.04509],"tcp_to_object_dist_end":0.02894,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52904,0.03892,0.016],"object_pos_start":[0.46645,-0.02595,0.14539],"object_to_goal_dist_end":0.22024,"object_to_goal_dist_start":0.28741,"object_z_max":0.17213,"peak_contact_force":0.12329,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14817.0,"raw_peak_contact_force":1.70739,"subtask_id":"transport_arc","tcp_end":[0.51902,0.06442,0.213],"tcp_start":[0.45441,-0.02573,0.17171],"tcp_to_object_dist_end":0.1989,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52903,0.03894,0.01602],"object_pos_start":[0.52904,0.03892,0.016],"object_to_goal_dist_end":0.22022,"object_to_goal_dist_start":0.22024,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":800.0,"raw_peak_contact_force":0.12326,"subtask_id":"release_1","tcp_end":[0.51418,0.06387,0.23715],"tcp_start":[0.51902,0.06442,0.213],"tcp_to_object_dist_end":0.22303,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69048,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09136,"approach_1.speed":0.07902,"descend_1.grasp_z_offset":-0.00984,"descend_1.speed":0.04637,"grasp_1.grip_force":18.94392,"lift_1.lift_height":0.13689,"lift_1.speed":0.08857,"release_1.duration":0.69736,"transport_1.arc_height":0.06166,"transport_1.transport_height":0.12588,"transport_1.transport_speed":0.10177},"optimized_scores":{"best_composite_score":-0.11711,"best_fitness_score":0.55289,"best_task_score":0.18846},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2699.0,"contact_point_centroid":[0.55869,0.00273,-0.00234],"force_p95":0.12457,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.28023,"mean_force":0.13805,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54314,0.01128,0.2129]},{"body_a":"world","body_b":"grasp_target","contact_count":172.0,"contact_point_centroid":[0.54286,0.00081,-0.00116],"force_p95":0.20345,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.31151,"mean_force":0.0473,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52793,0.00085,0.05004]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10405.0,"contact_point_centroid":[0.53563,-0.01851,0.09448],"force_p95":0.07475,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23711,"mean_force":0.04579,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53178,0.00084,0.09426]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10689.0,"contact_point_centroid":[0.53581,0.0202,0.09416],"force_p95":0.07338,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22958,"mean_force":0.04537,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53171,0.00084,0.09368]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1802.0,"contact_point_centroid":[0.543,0.02005,0.15759],"force_p95":0.11584,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22123,"mean_force":0.07256,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53667,0.00106,0.16096]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1897.0,"contact_point_centroid":[0.5431,-0.01787,0.15753],"force_p95":0.11288,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21464,"mean_force":0.06895,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53663,0.00106,0.16111]},{"body_a":"world","body_b":"grasp_target","contact_count":1612.0,"contact_point_centroid":[0.54431,0.00111,-0.00203],"force_p95":0.13193,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1528,"mean_force":0.12505,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53062,0.0009,0.0501]},{"body_a":"world","body_b":"grasp_target","contact_count":2332.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51728,0.00049,0.2132]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53587,0.00099,0.08085]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55886,0.00274,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54834,0.02291,0.24472]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3515.0,"contact_point_centroid":[0.53014,-0.01862,0.04964],"force_p95":0.04962,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1007,"mean_force":0.0278,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52929,0.00088,0.04851]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3933.0,"contact_point_centroid":[0.53034,0.02037,0.04941],"force_p95":0.04844,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0822,"mean_force":0.02517,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52929,0.00088,0.04851]}],"total_contact_groups":12},"final_pose_error":0.18197,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.55886,0.00274,0.01602],"final_tcp_position":[0.55153,0.023,0.24195],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.28023,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":584.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2332.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53702,0.001,0.12818],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10242,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53726,0.00101,0.05811],"tcp_start":[0.53702,0.001,0.12818],"tcp_to_object_dist_end":0.03286,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54422,0.00095,0.02586],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25038,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13169,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9060.0,"raw_peak_contact_force":0.1528,"subtask_id":"grasp_1","tcp_end":[0.52925,0.00088,0.04846],"tcp_start":[0.53726,0.00101,0.05811],"tcp_to_object_dist_end":0.02711,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.54918,0.00108,0.12076],"object_pos_start":[0.54422,0.00095,0.02586],"object_to_goal_dist_end":0.19822,"object_to_goal_dist_start":0.25038,"object_z_max":0.12065,"peak_contact_force":0.0605,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21266.0,"raw_peak_contact_force":0.31151,"tcp_end":[0.53941,0.00088,0.1508],"tcp_start":[0.52925,0.00088,0.04846],"tcp_to_object_dist_end":0.03159,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55886,0.00274,0.01602],"object_pos_start":[0.54918,0.00108,0.12076],"object_to_goal_dist_end":0.25033,"object_to_goal_dist_start":0.19822,"object_z_max":0.14144,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6398.0,"raw_peak_contact_force":1.28023,"subtask_id":"transport_arc","tcp_end":[0.55153,0.023,0.24195],"tcp_start":[0.53941,0.00088,0.1508],"tcp_to_object_dist_end":0.22695,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55886,0.00274,0.01602],"object_pos_start":[0.55886,0.00274,0.01602],"object_to_goal_dist_end":0.25033,"object_to_goal_dist_start":0.25033,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":800.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.54711,0.02282,0.26512],"tcp_start":[0.55153,0.023,0.24195],"tcp_to_object_dist_end":0.25018,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```