## Search State

- **Seed**: 2
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → approach → descend → retract → release → retract | linear_cartesian | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.2507 | 0.23 | ❌ rejected |
| 11 | approach → descend → grasp → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | 0.1207 | 0.40 | ❌ rejected |
| 10 | approach → descend → grasp → approach → descend → release | linear_cartesian | linear_cartesian | — | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0919 | 0.39 | ❌ rejected |
| 9 | approach → descend → grasp → approach → descend | linear_cartesian | linear_cartesian | — | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 9 | 0.3153 | 0.77 | ❌ rejected |
| 8 | approach → descend → grasp → approach → descend | linear_cartesian | linear_cartesian | — | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 9 | 0.4332 | 1.00 | ❌ rejected |

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

## Current Skill (Q=-0.251) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
phases:
- id: approach
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
      - 0.03
      - 0.1
      default: 0.05
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
  subtask_id: approach_1
- id: descend
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
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: descend_1
- id: grasp
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
  subtask_id: grasp_1
- id: transport
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
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
    placement_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: place_descend
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
    - 0.03
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    placement_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **transport** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - placement_z_offset: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **place_descend** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - placement_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: -0.251
- **task_score** (E): 0.227
- **fitness_score**: 0.579  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.830

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2015 |
| descend | 1.00 | 1.00 | 0.0516 |
| grasp | 1.00 | 1.00 | 0.0115 |
| transport | 0.67 | 1.00 | 0.2785 |
| place_descend | 1.00 | 1.00 | 0.0764 |
| pre_release_lift | 1.00 | 1.00 | 0.0258 |
| release | 1.00 | 1.00 | 0.0203 |
| retract | 0.33 | 1.00 | 0.0951 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.490, -0.014, 0.103) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 7.509 | 0.138 |
| descend | descend | 1.00 / step_budget | (0.490, -0.014, 0.103)→(0.488, -0.015, 0.052) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.488, -0.015, 0.052)→(0.480, -0.015, 0.043) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 44.000 | 0.136 | 0.176 |
| transport | approach | 0.67 / step_budget | (0.480, -0.015, 0.043)→(0.599, 0.135, 0.233) | (0.493, -0.015, 0.026)→(0.532, 0.042, 0.016) | 0.281→0.232 | 1.00 / 8.000 | 3249.632 | 1.800 |
| place_descend | descend | 1.00 / step_budget | (0.599, 0.135, 0.233)→(0.629, 0.169, 0.172) | (0.532, 0.042, 0.016)→(0.532, 0.042, 0.016) | 0.232→0.232 | 1.00 / 8.333 | 91002.530 | 0.123 |
| pre_release_lift | retract | 1.00 / step_budget | (0.629, 0.169, 0.172)→(0.625, 0.168, 0.197) | (0.532, 0.042, 0.016)→(0.532, 0.042, 0.016) | 0.232→0.232 | 1.00 / 8.667 | 182002.802 | 0.123 |
| release | release | 1.00 / step_budget | (0.625, 0.168, 0.197)→(0.620, 0.167, 0.217) | (0.532, 0.042, 0.016)→(0.532, 0.042, 0.016) | 0.232→0.232 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 0.33 / step_budget | (0.620, 0.167, 0.217)→(0.618, 0.166, 0.312) | (0.532, 0.042, 0.016)→(0.532, 0.042, 0.016) | 0.232→0.232 | 1.00 / 4.000 | 27.129 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.282
- phase_score: 0.507
- phase_breakdown.transport_arc_score: 0.240
- phase_breakdown.approach_1_score: 0.260
- phase_breakdown.release_1_score: 0.808
- phase_breakdown.descend_1_score: 0.913
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.608

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.608
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.282
- **Median Q (composite search score)**: -0.223
- **K-run variance**: 0.0015
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.287


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.33704,"average_solve_count":270.0,"average_success_count":270.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.07723,"approach.speed":0.05643,"descend.grasp_z_offset":0.02092,"descend.speed":0.06466,"place_descend.place_speed":0.04904,"place_descend.placement_z_offset":0.00358,"pre_release_lift.lift_height":0.03019,"pre_release_lift.lift_speed":0.06626,"release.release_duration":0.83189,"retract.retract_speed":0.0552,"transport.arc_height":0.15894,"transport.placement_z_offset":0.06173,"transport.transport_speed":0.09647},"optimized_scores":{"best_composite_score":-0.30629,"best_fitness_score":0.52371,"best_task_score":0.12437},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1866.0,"contact_point_centroid":[0.47205,-0.04499,-0.00257],"force_p95":0.3231,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.90037,"mean_force":0.15113,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.49942,0.02037,0.2714]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6838.0,"contact_point_centroid":[0.44647,-0.01886,0.1142],"force_p95":0.13139,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.48738,"mean_force":0.07384,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.44375,-0.03767,0.11362]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6986.0,"contact_point_centroid":[0.44629,-0.05646,0.11605],"force_p95":0.14159,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35789,"mean_force":0.0747,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.44387,-0.03756,0.11601]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02009,-0.00205],"force_p95":0.13764,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17757,"mean_force":0.12662,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46504,-0.01959,0.04885]},{"body_a":"world","body_b":"grasp_target","contact_count":2388.0,"contact_point_centroid":[0.47616,-0.02015,-0.00194],"force_p95":0.13091,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48619,-0.00908,0.20837]},{"body_a":"world","body_b":"grasp_target","contact_count":836.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.47173,-0.01909,0.08609]},{"body_a":"world","body_b":"grasp_target","contact_count":2748.0,"contact_point_centroid":[0.47207,-0.04598,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.59027,0.11837,0.24137]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.47207,-0.04598,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"pre_release_lift","phase_type":"retract","tcp_position_centroid":[0.62021,0.15275,0.19734]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.47207,-0.04598,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61649,0.15161,0.21071]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47207,-0.04598,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61271,0.15041,0.27242]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4841.0,"contact_point_centroid":[0.46343,-0.00031,0.04959],"force_p95":0.06786,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09912,"mean_force":0.045,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46395,-0.01956,0.04775]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5390.0,"contact_point_centroid":[0.46348,-0.03878,0.04932],"force_p95":0.06499,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08158,"mean_force":0.041,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46395,-0.01956,0.04775]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1681.0,"contact_point_centroid":[0.50636,0.02747,0.28748],"force_p95":0.01187,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01649,"mean_force":0.01073,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.50614,0.02747,0.28517]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2956.0,"contact_point_centroid":[0.59072,0.11846,0.24354],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01275,"mean_force":0.01037,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.59035,0.11845,0.24124]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2177.0,"contact_point_centroid":[0.62066,0.15277,0.19966],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.0105,"phase_index":5.0,"phase_name":"pre_release_lift","phase_type":"retract","tcp_position_centroid":[0.62021,0.15275,0.19734]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.61937,0.15237,0.20985],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0127,"mean_force":0.01006,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61891,0.15235,0.20734]}],"total_contact_groups":16},"final_pose_error":0.06238,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.47207,-0.04598,0.01602],"final_tcp_position":[0.61318,0.15048,0.31776],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273004.11064,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":598.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2388.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47405,-0.01854,0.1167],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09072,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":209.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":836.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47152,-0.01973,0.05553],"tcp_start":[0.47405,-0.01854,0.1167],"tcp_to_object_dist_end":0.02987,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47609,-0.01971,0.0258],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28827,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13655,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12031.0,"raw_peak_contact_force":0.17757,"subtask_id":"grasp_1","tcp_end":[0.46392,-0.01956,0.04772],"tcp_start":[0.47152,-0.01973,0.05553],"tcp_to_object_dist_end":0.02507,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47207,-0.04598,0.01602],"object_pos_start":[0.47609,-0.01971,0.0258],"object_to_goal_dist_end":0.31267,"object_to_goal_dist_start":0.28827,"object_z_max":0.17406,"peak_contact_force":9748.6496,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17371.0,"raw_peak_contact_force":1.90037,"subtask_id":"transport_arc","tcp_end":[0.55686,0.081,0.30063],"tcp_start":[0.46392,-0.01956,0.04772],"tcp_to_object_dist_end":0.32298,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":687.0,"n_steps_budget":1000.0,"object_pos_end":[0.47207,-0.04598,0.01602],"object_pos_start":[0.47207,-0.04598,0.01602],"object_to_goal_dist_end":0.31267,"object_to_goal_dist_start":0.31267,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5704.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.62348,0.15364,0.19113],"tcp_start":[0.55686,0.081,0.30063],"tcp_to_object_dist_end":0.30568,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.47207,-0.04598,0.01602],"object_pos_start":[0.47207,-0.04598,0.01602],"object_to_goal_dist_end":0.31267,"object_to_goal_dist_start":0.31267,"object_z_max":0.01602,"peak_contact_force":273004.11064,"phase_name":"pre_release_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4229.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62007,0.15266,0.21019],"tcp_start":[0.62348,0.15364,0.19113],"tcp_to_object_dist_end":0.31475,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47207,-0.04598,0.01602],"object_pos_start":[0.47207,-0.04598,0.01602],"object_to_goal_dist_end":0.31267,"object_to_goal_dist_start":0.31267,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61513,0.15117,0.23011],"tcp_start":[0.62007,0.15266,0.21019],"tcp_to_object_dist_end":0.32429,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47207,-0.04598,0.01602],"object_pos_start":[0.47207,-0.04598,0.01602],"object_to_goal_dist_end":0.31267,"object_to_goal_dist_start":0.31267,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61318,0.15048,0.31776],"tcp_start":[0.61513,0.15117,0.23011],"tcp_to_object_dist_end":0.38672,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28745,"average_solve_count":247.0,"average_success_count":247.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.05774,"approach.speed":0.05739,"descend.grasp_z_offset":0.01614,"descend.speed":0.04133,"place_descend.place_speed":0.05917,"place_descend.placement_z_offset":0.00464,"pre_release_lift.lift_height":0.03988,"pre_release_lift.lift_speed":0.03914,"release.release_duration":1.67869,"retract.retract_speed":0.05987,"transport.arc_height":0.11989,"transport.placement_z_offset":0.0322,"transport.transport_speed":0.10631},"optimized_scores":{"best_composite_score":-0.22246,"best_fitness_score":0.60754,"best_task_score":0.28214},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1731.0,"contact_point_centroid":[0.52761,0.07553,-0.00259],"force_p95":0.2994,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.80237,"mean_force":0.15168,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55154,0.1109,0.19562]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7875.0,"contact_point_centroid":[0.46066,0.01098,0.11674],"force_p95":0.10499,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31035,"mean_force":0.06622,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.45731,-0.00791,0.11431]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7747.0,"contact_point_centroid":[0.45847,-0.02921,0.11197],"force_p95":0.11511,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29362,"mean_force":0.06645,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.45549,-0.01022,0.10982]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02622,-0.00207],"force_p95":0.14333,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1971,"mean_force":0.12828,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44783,-0.02547,0.0449]},{"body_a":"world","body_b":"grasp_target","contact_count":2660.0,"contact_point_centroid":[0.45856,-0.02632,-0.00194],"force_p95":0.12957,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.4779,-0.01201,0.19831]},{"body_a":"world","body_b":"grasp_target","contact_count":668.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.45483,-0.025,0.07432]},{"body_a":"world","body_b":"grasp_target","contact_count":1024.0,"contact_point_centroid":[0.5306,0.07978,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61249,0.19068,0.14319]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.5306,0.07978,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"pre_release_lift","phase_type":"retract","tcp_position_centroid":[0.61803,0.20104,0.12857]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5306,0.07978,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61356,0.19939,0.14636]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5306,0.07978,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.60872,0.19758,0.21016]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4796.0,"contact_point_centroid":[0.44673,-0.00622,0.04634],"force_p95":0.06888,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10634,"mean_force":0.04521,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44676,-0.02543,0.04388]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5178.0,"contact_point_centroid":[0.44663,-0.04466,0.04573],"force_p95":0.06763,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.06928,"mean_force":0.04286,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44677,-0.02543,0.04388]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1556.0,"contact_point_centroid":[0.56194,0.12377,0.20384],"force_p95":0.0114,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01645,"mean_force":0.01063,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56167,0.12377,0.20162]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2426.0,"contact_point_centroid":[0.61852,0.20106,0.13083],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.01052,"phase_index":5.0,"phase_name":"pre_release_lift","phase_type":"retract","tcp_position_centroid":[0.61803,0.20103,0.12858]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1083.0,"contact_point_centroid":[0.61278,0.19072,0.1455],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01275,"mean_force":0.01053,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61252,0.19071,0.14312]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.61714,0.20052,0.1455],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01108,"mean_force":0.01008,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61654,0.20049,0.14316]}],"total_contact_groups":16},"final_pose_error":0.05685,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.5306,0.07978,0.01602],"final_tcp_position":[0.60914,0.19768,0.25888],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":666.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2660.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45737,-0.02441,0.09723],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07125,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":167.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":668.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45419,-0.0257,0.05112],"tcp_start":[0.45737,-0.02441,0.09723],"tcp_to_object_dist_end":0.02549,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4585,-0.02566,0.02573],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30326,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.1406,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11774.0,"raw_peak_contact_force":0.1971,"subtask_id":"grasp_1","tcp_end":[0.44674,-0.02543,0.04385],"tcp_start":[0.45419,-0.0257,0.05112],"tcp_to_object_dist_end":0.0216,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5306,0.07978,0.01602],"object_pos_start":[0.4585,-0.02566,0.02573],"object_to_goal_dist_end":0.1898,"object_to_goal_dist_start":0.30326,"object_z_max":0.15877,"peak_contact_force":0.12263,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18909.0,"raw_peak_contact_force":1.80237,"subtask_id":"transport_arc","tcp_end":[0.60511,0.17911,0.17439],"tcp_start":[0.44674,-0.02543,0.04385],"tcp_to_object_dist_end":0.20125,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":256.0,"n_steps_budget":1000.0,"object_pos_end":[0.5306,0.07978,0.01602],"object_pos_start":[0.5306,0.07978,0.01602],"object_to_goal_dist_end":0.1898,"object_to_goal_dist_start":0.1898,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2107.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.62204,0.20242,0.11802],"tcp_start":[0.60511,0.17911,0.17439],"tcp_to_object_dist_end":0.18386,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.5306,0.07978,0.01602],"object_pos_start":[0.5306,0.07978,0.01602],"object_to_goal_dist_end":0.1898,"object_to_goal_dist_start":0.1898,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"pre_release_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4718.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61792,0.20096,0.14606],"tcp_start":[0.62204,0.20242,0.11802],"tcp_to_object_dist_end":0.19803,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5306,0.07978,0.01602],"object_pos_start":[0.5306,0.07978,0.01602],"object_to_goal_dist_end":0.1898,"object_to_goal_dist_start":0.1898,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61183,0.19873,0.16566],"tcp_start":[0.61792,0.20096,0.14606],"tcp_to_object_dist_end":0.2077,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5306,0.07978,0.01602],"object_pos_start":[0.5306,0.07978,0.01602],"object_to_goal_dist_end":0.1898,"object_to_goal_dist_start":0.1898,"object_z_max":0.01602,"peak_contact_force":81.14225,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60914,0.19768,0.25888],"tcp_start":[0.61183,0.19873,0.16566],"tcp_to_object_dist_end":0.28116,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.27692,"average_solve_count":260.0,"average_success_count":260.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.05892,"approach.speed":0.03615,"descend.grasp_z_offset":0.01524,"descend.speed":0.05495,"place_descend.place_speed":0.05292,"place_descend.placement_z_offset":0.01352,"pre_release_lift.lift_height":0.04213,"pre_release_lift.lift_speed":0.04656,"release.release_duration":1.05667,"retract.retract_speed":0.06534,"transport.arc_height":0.05205,"transport.placement_z_offset":0.04306,"transport.transport_speed":0.14262},"optimized_scores":{"best_composite_score":-0.22331,"best_fitness_score":0.60669,"best_task_score":0.27435},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1243.0,"contact_point_centroid":[0.59143,0.08692,-0.00271],"force_p95":0.49068,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.69791,"mean_force":0.16578,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.60222,0.10076,0.19927]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6013.0,"contact_point_centroid":[0.54284,-0.00098,0.10075],"force_p95":0.13133,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34261,"mean_force":0.08053,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.53854,0.01772,0.09925]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5985.0,"contact_point_centroid":[0.54261,0.03643,0.10031],"force_p95":0.12997,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31868,"mean_force":0.08103,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.53853,0.01766,0.09868]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00103,-0.00203],"force_p95":0.13244,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15327,"mean_force":0.12546,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53067,0.00089,0.04006]},{"body_a":"world","body_b":"grasp_target","contact_count":2948.0,"contact_point_centroid":[0.54431,0.00113,-0.00195],"force_p95":0.12851,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12279,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51722,0.00049,0.19695]},{"body_a":"world","body_b":"grasp_target","contact_count":640.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.53649,0.00099,0.07213]},{"body_a":"world","body_b":"grasp_target","contact_count":268.0,"contact_point_centroid":[0.59449,0.09359,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.63773,0.14878,0.21553]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.59449,0.09359,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"pre_release_lift","phase_type":"retract","tcp_position_centroid":[0.63696,0.15115,0.21709]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59449,0.09359,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63378,0.15016,0.23628]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.59449,0.09359,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.63063,0.14913,0.30576]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4114.0,"contact_point_centroid":[0.5306,-0.01834,0.0413],"force_p95":0.07627,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1222,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52945,0.00086,0.03863]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4879.0,"contact_point_centroid":[0.53053,0.01994,0.04043],"force_p95":0.06834,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08897,"mean_force":0.04469,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52945,0.00086,0.03863]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1042.0,"contact_point_centroid":[0.61199,0.11326,0.21546],"force_p95":0.01278,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01584,"mean_force":0.0107,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.61161,0.11325,0.21321]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2323.0,"contact_point_centroid":[0.63744,0.15117,0.21932],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01275,"mean_force":0.01041,"phase_index":5.0,"phase_name":"pre_release_lift","phase_type":"retract","tcp_position_centroid":[0.63696,0.15115,0.21707]},{"body_a":"left_finger","body_b":"right_finger","contact_count":289.0,"contact_point_centroid":[0.63789,0.1488,0.2179],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01098,"mean_force":0.01036,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.63773,0.14878,0.21554]},{"body_a":"left_finger","body_b":"right_finger","contact_count":227.0,"contact_point_centroid":[0.63649,0.15084,0.23558],"force_p95":0.01087,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0109,"mean_force":0.00987,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.63594,0.15082,0.23328]}],"total_contact_groups":16},"final_pose_error":0.04554,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.59449,0.09359,0.01602],"final_tcp_position":[0.63121,0.14923,0.35992],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273007.34576,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":738.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":22.28147,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2948.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53717,0.001,0.09587],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07022,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":160.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":640.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53791,0.00102,0.04867],"tcp_start":[0.53717,0.001,0.09587],"tcp_to_object_dist_end":0.02353,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5442,0.00076,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.2505,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13064,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15327,"subtask_id":"grasp_1","tcp_end":[0.52942,0.00086,0.03859],"tcp_start":[0.53791,0.00102,0.04867],"tcp_to_object_dist_end":0.0195,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":862.0,"n_steps_budget":1000.0,"object_pos_end":[0.59449,0.09359,0.01602],"object_pos_start":[0.5442,0.00076,0.02587],"object_to_goal_dist_end":0.194,"object_to_goal_dist_start":0.2505,"object_z_max":0.14547,"peak_contact_force":0.12263,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14283.0,"raw_peak_contact_force":1.69791,"subtask_id":"transport_arc","tcp_end":[0.6363,0.14581,0.22363],"tcp_start":[0.52942,0.00086,0.03859],"tcp_to_object_dist_end":0.21812,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":67.0,"n_steps_budget":1000.0,"object_pos_end":[0.59449,0.09359,0.01602],"object_pos_start":[0.59449,0.09359,0.01602],"object_to_goal_dist_end":0.194,"object_to_goal_dist_start":0.194,"object_z_max":0.01602,"peak_contact_force":273007.34576,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":557.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.64001,0.15198,0.20665],"tcp_start":[0.6363,0.14581,0.22363],"tcp_to_object_dist_end":0.20451,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.59449,0.09359,0.01602],"object_pos_start":[0.59449,0.09359,0.01602],"object_to_goal_dist_end":0.194,"object_to_goal_dist_start":0.194,"object_z_max":0.01602,"peak_contact_force":273004.17322,"phase_name":"pre_release_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4491.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63697,0.1511,0.23625],"tcp_start":[0.64001,0.15198,0.20665],"tcp_to_object_dist_end":0.23154,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59449,0.09359,0.01602],"object_pos_start":[0.59449,0.09359,0.01602],"object_to_goal_dist_end":0.194,"object_to_goal_dist_start":0.194,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6326,0.14977,0.25543],"tcp_start":[0.63697,0.1511,0.23625],"tcp_to_object_dist_end":0.24885,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59449,0.09359,0.01602],"object_pos_start":[0.59449,0.09359,0.01602],"object_to_goal_dist_end":0.194,"object_to_goal_dist_start":0.194,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63121,0.14923,0.35992],"tcp_start":[0.6326,0.14977,0.25543],"tcp_to_object_dist_end":0.3503,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```